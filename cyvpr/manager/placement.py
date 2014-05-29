import os.path
import re

import tables as ts
from path_helpers import path
from cyvpr.Main import cMain
from .table_layouts import NET_FILES_TABLE_LAYOUT, get_PLACEMENT_TABLE_LAYOUT



def require_paths(fn):
    def wrapped(self, *args, **kwargs):
        if self.paths_database is None:
            raise ValueError, 'Paths database must be provided.'
        return fn(self, *args, **kwargs)
    return wrapped


class PlacementManager(object):
    def __init__(self, placement_database, paths_database=None, mode='r'):
        self.placement_database = placement_database
        filters = ts.Filters(complib='blosc', complevel=2)
        self.h5f = {'placements': ts.openFile(placement_database, mode,
                                              filters=filters)}
        self.paths_database = paths_database
        if self.paths_database:
            self.h5f['paths'] = ts.openFile(paths_database, 'r')

    @require_paths
    def sync_net_files_from_paths(self, arch_path):
        vpr_main = cMain()
        h5f = self.h5f['placements']
        if not hasattr(h5f.root, 'net_files'):
            table = h5f.createTable(h5f.root, 'net_files', NET_FILES_TABLE_LAYOUT)
            table.cols.md5.createCSIndex()
        net_files = h5f.root.net_files
        for net_file_path in self.h5f['paths'].root.net_file_paths:
            if net_file_path['md5'] not in net_files.cols.md5:
                # Intialize VPR with dummy output files to read in net-file to
                # get block-count and net-count.
                vpr_main.init([net_file_path['path'], arch_path, 'placed.out',
                               'routed.out', '-place_only', '-nodisp'])
                row = net_files.row
                row['md5'] = net_file_path['md5']
                row['block_count'] = vpr_main.block_count
                row['net_count'] = vpr_main.net_count
                row.append()
        net_files.flush()

    @require_paths
    def sync_placements_from_paths(self, arch_path):
        self.sync_net_files_from_paths(arch_path)
        vpr_main = cMain()
        h5f = self.h5f['placements']
        if not hasattr(h5f.root, 'placement_results'):
            h5f.createGroup(h5f.root, 'placement_results')
        placement_results = h5f.root.placement_results
        cre_net_file_name = re.compile(r'(?P<net_file_namebase>[^\/\s]+)\.net')
        for placement_path in self.h5f['paths'].root.placement_paths:
            with open(placement_path['path'], 'rb') as f:
                header = f.readline()
            match = cre_net_file_name.search(header)
            net_file_namebase = match.group('net_file_namebase')
            net_file_name = net_file_namebase + '.net'
            if hasattr(placement_results, net_file_namebase):
                placement_table = getattr(placement_results, net_file_namebase)
                if (placement_path['block_positions_sha1'] in
                    placement_table.cols.block_positions_sha1):
                    # This placement has already been entered into the table.
                    continue

            # The placement has not been entered into the results table, so
            # process it now.
            net_file = None
            for net_file_data in self.h5f['paths'].root.net_file_paths:
                if net_file_data['path'].endswith(net_file_name):
                    # The net-file used for the placement is available.
                    net_file = net_file_data
                    break
            if net_file is None:
                raise RuntimeError, 'The net-file used for the placement is _not_ available.'

            # Parse using VPR.
            block_positions = (vpr_main
                                .read_placement(net_file_data['path'],
                                                arch_path,
                                                placement_path['path']))
            if not hasattr(placement_results, net_file_namebase):
                table = h5f.createTable(placement_results, net_file_namebase,
                                        get_PLACEMENT_TABLE_LAYOUT(
                                                vpr_main.block_count))
                table.cols.net_file_md5.createIndex()
                table.cols.block_positions_sha1.createIndex()
            placements = getattr(placement_results, net_file_namebase)
            row = placements.row
            row['net_file_md5'] = net_file['md5']
            row['block_positions_sha1'] = placement_path['block_positions_sha1']
            row['block_positions'] = block_positions
            row.append()
            placements.flush()

    def md5s_by_net_file_namebase(self, vpr_net_file_namebase):
        placement_results = getattr(self.h5f['placements'].root.placements,
                                    vpr_net_file_namebase)
        return placement_results.placements.cols.md5[:]

    @require_paths
    def paths_by_net_file_namebase(self, vpr_net_file_namebase):
        placement_results = getattr(self.h5f['placements'].root.placements,
                                    vpr_net_file_namebase)
        paths = []
        for x in placement_results.placements:
            paths.append(self.path_by_md5(x['md5']))
        return paths

    @require_paths
    def path_by_md5(self, md5):
        matches = [path(placed_file['path'])
                   for placed_file in (self.h5f['paths'].root.placement_paths
                                       .where('md5 == "%s"' % md5))]
        if not matches:
            raise KeyError, 'No placement path found for MD5: %s' % md5
        return matches[0]

    @require_paths
    def md5_by_path(self, file_path):
        if file_path != path(file_path).abspath():
            raise ValueError, ('Paths must be absolute paths.  `%s` is not.'
                               % file_path)
        matches = [placed_file['md5']
                   for placed_file in (self.h5f['paths'].root.placement_paths
                                       .where('path == "%s"' % file_path))]
        if not matches:
            raise KeyError, 'No placement path found for file-path: %s' % file_path
        return matches[0]

    @require_paths
    def net_file_path_by_id(self, net_file_id):
        net_file_md5 = self.h5f['placements'].root.net_files[net_file_id]['md5']
        return self.net_file_path_by_md5(net_file_md5)

    @require_paths
    def net_file_path_by_md5(self, net_file_md5):
        matches = [path(net_file['path'])
                   for net_file in (self.h5f['paths'].root.net_file_paths
                                    .where('md5 == "%s"' % net_file_md5))]
        if not matches:
            raise KeyError, 'No net-file found with MD5: %s' % net_file_md5
        return matches[0]

    @require_paths
    def net_file_by_placement_md5(self, placement_md5):
        placement = self.placement_by_md5(placement_md5)
        return self.h5f['placements'].root.net_files[placement['net_file_id']]

    @require_paths
    def placement_by_md5(self, md5):
        h5f = self.h5f['placements']
        placement_results = h5f.root.placements
        for table in h5f.walkNodes(placement_results, 'Table'):
            if hasattr(table.cols, 'md5'):
                for x in table.where('md5 == "%s"' % md5):
                    return x.fetch_all_fields()
        return None

    def paths_by_placement_md5(self, md5):
        placement_data = self.placement_by_md5(md5)
        return (self.net_file_path_by_id(placement_data['net_file_id']),
                self.path_by_md5(md5))

    def __del__(self):
        for f in self.h5f.values():
            f.close()
