import re
import hashlib
import tables as ts
from path_helpers import path
from cyvpr.Main import cMain


def process_placement_path(net_file_paths_table, placement_paths_table,
                           file_path, architecture, update):
    vpr_main = cMain()
    cre_net_file_name = re.compile(r'(?P<net_file_namebase>[^\/\s]+)\.net')
    with open(file_path, 'rb') as f:
        header = f.readline()
    match = cre_net_file_name.search(header)
    net_file_namebase = match.group('net_file_namebase')
    net_file_name = net_file_namebase + '.net'

    # The placement has not been entered into the results table, so
    # process it now.
    net_file = None
    for net_file_data in net_file_paths_table:
        if net_file_data['path'].endswith(net_file_name):
            # The net-file used for the placement is available.
            net_file = net_file_data
            break
    if net_file is None:
        raise RuntimeError, ('The net-file used for the placement is _not_ '
                             'available.')

    # Parse using VPR.
    block_positions = vpr_main.read_placement(net_file['path'], architecture,
                                              file_path)
    sha1 = hashlib.sha1()
    sha1.update(block_positions.data)
    block_positions_sha1 = sha1.hexdigest()

    row_count = 0
    for row in placement_paths_table.where('block_positions_sha1 == "%s"'
                                           % block_positions_sha1):
        # The table already contains an entry for this file.
        print ('The table already contains block_positions with this SHA1: %s'
               % block_positions_sha1)
        if update and not row['path'] == file_path.abspath():
            row['path'] = file_path.abspath()
            row.update()
            print '  \--> updated path to: %s' % row['path']
        row_count += 1

    if row_count == 0:
        row = placement_paths_table.row
        row['block_positions_sha1'] = block_positions_sha1
        row['path'] = file_path.abspath()
        row.append()


def process_net_file_path(paths_table, file_path, update):
    md5 = file_path.read_hexhash('md5')

    row_count = 0
    for row in paths_table.where('md5 == "%s"' % md5):
        # The table already contains an entry for this file.
        print ('The table already contains a file with this MD5: %s' %
               md5)
        if update and not row['path'] == file_path.abspath():
            row['path'] = file_path.abspath()
            row.update()
            print '  \--> updated path to: %s' % row['path']
        row_count += 1

    if row_count == 0:
        row = paths_table.row
        row['md5'] = md5
        row['path'] = file_path.abspath()
        row.append()


def main(paths_database_path, net_file_paths, placement_file_paths,
         architecture, update=False):
    local_h5f = ts.openFile(paths_database_path, 'a')

    if hasattr(local_h5f.root, 'placement_paths'):
        placement_paths_table = local_h5f.root.placement_paths
    else:
        placement_paths_table = local_h5f.createTable(
                local_h5f.root, 'placement_paths', {'block_positions_sha1':
                                                    ts.StringCol(40, pos=0),
                                                    'path': ts.StringCol(500)})

    if hasattr(local_h5f.root, 'net_file_paths'):
        net_file_paths_table = local_h5f.root.net_file_paths
    else:
        net_file_paths_table = local_h5f.createTable(local_h5f.root,
                                                'net_file_paths',
                                                {'md5': ts.StringCol(32,
                                                                     pos=0),
                                                 'path': ts.StringCol(500)})

    # Create indexes for columns
    for table in (placement_paths_table, net_file_paths_table):
        for col_name in ('path', ):
            col = getattr(table.cols, col_name)
            if col.index is None:
                col.createIndex()

    col = getattr(net_file_paths_table.cols, 'md5')
    if col.index is None:
        col.createCSIndex()

    col = getattr(placement_paths_table.cols, 'block_positions_sha1')
    if col.index is None:
        col.createCSIndex()

    for net_file in net_file_paths:
        process_net_file_path(net_file_paths_table, net_file, update)

    net_file_paths_table.flush()

    for placement_file in placement_file_paths:
        process_placement_path(net_file_paths_table, placement_paths_table,
                               placement_file, architecture, update)

    placement_paths_table.flush()


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Register net-file or placement files '
                                        'in local database.')
    parser.add_argument('-a', '--architecture', default=None)
    parser.add_argument('-u', '--update', action='store_true', default=False)
    parser.add_argument(dest='paths_database', type=path)
    parser.add_argument(nargs='+', dest='paths', type=path)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    net_file_paths = [p for p in args.paths if p.ext == '.net']
    placement_paths = [p for p in args.paths if p.ext == '.out']
    if placement_paths and args.architecture is None:
        raise RuntimeError, ('If placement files are provided, an architecture'
                             ' file must be specified.')
    main(str(args.paths_database), net_file_paths, placement_paths,
         args.architecture, args.update)
