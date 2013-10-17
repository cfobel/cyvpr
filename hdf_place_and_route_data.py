import tables as ts

from path import path
from vpr_netfile_parser.VprNetParser import cVprNetFileParser
from cyvpr.Main import cMain


NET_FILES_TABLE_LAYOUT = {'id': ts.UInt64Col(pos=0),
                          'md5': ts.StringCol(32, pos=1),
                          'block_count': ts.UInt32Col(pos=2),
                          'net_count': ts.UInt32Col(pos=3)}
PLACEMENT_TABLE_LAYOUT = {'id': ts.UInt64Col(pos=0),
                          'net_file_id': ts.UInt64Col(pos=1),
                          'block_position_offset': ts.UInt64Col(pos=2),
                          'block_count': ts.UInt32Col(pos=3),
                          'md5': ts.StringCol(32, pos=4)}
BLOCK_POSITIONS_TABLE_LAYOUT = {'id': ts.UInt64Col(pos=0),
                                'placement_id': ts.UInt64Col(pos=1),
                                'position': {
                                    'x': ts.UInt32Col(pos=0),
                                    'y': ts.UInt32Col(pos=1),
                                    'slot_index':
                                    ts.UInt32Col(pos=2)}}
ROUTE_TABLE_LAYOUT = {'id': ts.UInt64Col(pos=0),
                      'net_file_id': ts.UInt64Col(pos=1),
                      'placement_file_id': ts.UInt64Col(pos=2),
                      'success': ts.BoolCol(pos=3),
                      'width_fac': ts.UInt32Col(pos=4),
                      'start': ts.Float64Col(pos=5),
                      'end': ts.Float64Col(pos=6),
                      'router_options': {'first_iter_pres_fac':
                                         ts.Float32Col(pos=0),
                                         'initial_pres_fac':
                                         ts.Float32Col(pos=1),
                                         'pres_fac_mult': ts.Float32Col(pos=2),
                                         'acc_fac': ts.Float32Col(pos=3),
                                         'bend_cost': ts.Float32Col(pos=4),
                                         'bb_factor': ts.Int32Col(pos=5),
                                         'astar_fac': ts.Float32Col(pos=6),
                                         'max_criticality':
                                         ts.Float32Col(pos=7),
                                         'criticality_exp':
                                         ts.Float32Col(pos=8), },
                      'net_data_offset': ts.UInt64Col(pos=8),
                      'net_count': ts.UInt32Col(pos=9)}
ROUTE_NET_DATA_TABLE_LAYOUT = {'id': ts.UInt64Col(pos=0),
                               'route_id': ts.UInt64Col(pos=1),
                               'net_data': {'bends': ts.UInt32Col(pos=0),
                                            'wire_length': ts.UInt32Col(pos=1),
                                            'segments': ts.UInt32Col(pos=2)}}

def create_init_data():
    # Open a file in "w"rite mode
    filters = ts.Filters(complib='blosc', complevel=2)
    fileh = ts.openFile("place_and_route_data.h5", mode="w", filters=filters)

    # Get the HDF5 root group
    root = fileh.root
    net_files = fileh.createTable(root, 'net_files',
                                  NET_FILES_TABLE_LAYOUT)
    net_paths = path('/var/benchmarks/mcnc').files('*.net')

    placements = fileh.createGroup(root, 'placements', 'Placements')

    m = cMain()

    for i, p in enumerate(net_paths):
        parser = cVprNetFileParser(p)
        net_file = net_files.row
        net_file['id'] = i
        net_file['md5'] = p.read_hexhash('md5')
        net_file['block_count'] = len(parser.block_labels)
        net_file['net_count'] = len(parser.net_labels)

        group = fileh.createGroup(placements, p.namebase,
                                'Placements for %s' % p.namebase)
        placement_table = fileh.createTable(group, 'placements',
                                            PLACEMENT_TABLE_LAYOUT)
        placement_table.flush()
        positions_table = fileh.createTable(
                group, 'block_positions', BLOCK_POSITIONS_TABLE_LAYOUT)
        positions_table.flush()

        placement_id = len(placement_table)
        positions_id = len(positions_table)
        for j, d in enumerate(path('../place_results')
                            .files('placed-%s-*.out' % p.namebase)):
            positions = m.read_placement(
                    p, '/var/benchmarks/4lut_sanitized.arch', d)

            k = 0
            placement = placement_table.row
            placement['id'] = placement_id + j
            placement['net_file_id'] = net_file['id']
            placement['block_position_offset'] = positions_id
            placement['block_count'] = net_file['block_count']
            placement['md5'] = d.read_hexhash('md5')

            for k, b in enumerate(positions):
                row = positions_table.row
                row['id'] = positions_id + k
                row['placement_id'] = placement['id']
                row['position'] = b
                row.append()
            positions_id += len(positions)
            placement.append()
            positions_table.flush()
            placement_table.flush()
        net_file.append()
        net_files.flush()
    fileh.close()


def load_routed_data():
    fileh = ts.openFile('place_and_route_data.h5', mode='r')

    # Get the HDF5 root group
    root = fileh.root
    route_paths = list(path('../route_results').files('routed-*.dat'))
    return fileh, root, [r.pickle_load() for r in route_paths[:2]]

if __name__ == '__main__':
    fileh, root, data = load_routed_data()
