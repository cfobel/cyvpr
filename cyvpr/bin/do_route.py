from cyvpr.Main import cMain
from cyvpr.Route import unix_time
import tables as ts
from path import path
from hdf_place_and_route_data import (ROUTE_TABLE_LAYOUT,
                                      ROUTE_NET_DATA_TABLE_LAYOUT)

def create_init_data(h5f, root):
    routings = h5f.createGroup(root, 'routings')


    # Iterate through each group of placements _(one group per net-file)_ and
    # create a corresponding routing group.
    #
    # __NB__ Each routing group
    # contains:
    #
    #  * A route-states table
    #  * A routing-per-net-data table
    for net_placements in h5f.iterNodes(root.placements, 'Group'):
        net_name = net_placements._v_name

        net_routings = h5f.createGroup(routings, net_name)
        h5f.createTable(net_routings, 'route_states', ROUTE_TABLE_LAYOUT,
                        'Routing states')
        h5f.createTable(net_routings, 'route_net_data',
                        ROUTE_NET_DATA_TABLE_LAYOUT,
                        'Routing per-net data')


def append_route_state(route_states, route_net_data, route_state, net_file_id,
                       placement_file_id):
    route_state_id = len(route_states)
    net_data_id = len(route_net_data)

    state_row = route_states.row
    state_row['id'] = route_state_id
    state_row['net_file_id'] = net_file_id
    state_row['placement_file_id'] = placement_file_id
    state_row['success'] = route_state.success
    state_row['width_fac'] = route_state.width_fac
    # Convert start-date-time to UTC unix timestamp
    state_row['start'] = unix_time(route_state.start)
    state_row['end'] = unix_time(route_state.end)

    s = route_state
    state_row['router_options'] = tuple(getattr(s.router_opts, attr)
                                        for attr in ('first_iter_pres_fac',
                                                     'initial_pres_fac',
                                                     'pres_fac_mult',
                                                     'acc_fac', 'bend_cost',
                                                     'bb_factor', 'astar_fac',
                                                     'max_criticality',
                                                     'criticality_exp'))
    state_row['net_count'] = len(s.bends)
    state_row['net_data_offset'] = net_data_id
    state_row.append()
    route_states.flush()

    for i in xrange(len(s.bends)):
        net_data = route_net_data.row
        net_data['id'] = net_data_id + i
        net_data['route_id'] = route_states[-1]['id']
        net_data['net_data'] = s.bends[i], s.wire_lengths[i], s.segments[i]
        net_data.append()
    route_net_data.flush()


def prepare_for_route(net_path, arch_path, placed_path):
    m = cMain()
    m.init([net_path, arch_path, placed_path, 'routed.out', '-nodisp',
            '-route_only'])
    m.read_placement(net_path, arch_path, placed_path)
    return m



def get_paths_by_md5():
    # Load all available VPR net-files, and create a mapping between the MD5
    # hash of each file to the path to the corresponding file.
    #
    # __NB__ This mapping is required to match against net-file records in the
    # HDF5 data file, since only MD5 hashes of each net-file are stored in the
    # HDF5 file, rather than file-paths.  This allows the actual net-files to
    # be moved, etc. without breaking the results data in the HDF5 file.
    net_paths = dict([(p.read_hexhash('md5'), p)
                    for p in path('/var/benchmarks/mcnc').files('*.net')])

    # Load all available placement output files, and create a mapping between
    # the MD5 hash of each file to the path to the corresponding file.
    #
    # __NB__ This mapping is required to match against placement records in the
    # HDF5 data file, since only MD5 hashes of each placement result file are
    # stored in the HDF5 file, rather than file-paths.  This allows the actual
    # placement output files to be moved, etc. without breaking the results
    # data in the HDF5 file.
    placement_paths = dict([(p.read_hexhash('md5'), p)
                            for p in path('../place_results').files('*.out')])

    return net_paths, placement_paths


#placement_infos = dict([(p['md5'], p)
                        #for p in net_placements.placements[:]])
#for info in placement_infos.values():
    #net_hash = root.net_files[info[1]][1]
    #net_file_id = root.net_files[info[1]][0]
    #net_path = net_paths[net_hash]

    #placed_id = info[0]
    #placed_hash = info[-1]
    #placed_path = placement_paths[placed_hash]


def get_place_net_info(net_files, placed_results, net_paths, placement_md5,
                       placement_path, net_name):
    placements_by_md5 = dict([(p['md5'], p)
                              for p in placed_results.placements[:]])
    placement_info = placements_by_md5[placement_md5]
    net_file_id = placement_info[1]
    net_file_md5 = net_files[net_file_id][1]
    net_path = net_paths[net_file_md5]
    return net_path, net_file_id



def do_route(route_database_path, paths_database_path, vpr_net_file_namebase,
             architecture, clbs_per_pin_factor, fast=True):
    h5f = ts.openFile(route_database_path, mode='a')
    try:
        create_init_data(h5f, h5f.root)
    except ts.NodeError:
        # Data already exists
        pass
    root = h5f.root
    local_h5f = ts.openFile(paths_database_path, 'r')
    net_file_paths = local_h5f.root.net_file_paths
    placement_paths = local_h5f.root.placement_paths
    placed_results = getattr(root.placements, vpr_net_file_namebase)
    routing_results = getattr(root.routings, vpr_net_file_namebase)
    if len(routing_results.route_states) > 0:
        h5f.close()
        raise SystemExit, 'Already routed'
    for placement_info in placed_results.placements:
        net_file_path = [row['path']
                         for row in net_file_paths
                         .where('md5 == "%s"' % root.net_files[placement_info
                                                               ['net_file_id']]
                                ['md5'])][0]
        placement_path = [row['path']
                          for row in placement_paths
                          .where('md5 == "%s"' % placement_info['md5'])][0]
        print 'Routing %s' % placement_path
        m = prepare_for_route(net_file_path, architecture, placement_path)
        m.route_again(clbs_per_pin_factor * m.pins_per_clb, fast=fast)
        states = m.most_recent_route_states()
        s = states[-1]
        append_route_state(routing_results.route_states,
                           routing_results.route_net_data, s,
                           placement_info['net_file_id'], placement_info['id'])
    h5f.close()


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description="""Run VPR route based on net-file namebase""")
    parser.add_argument('-f', '--fast', action='store_true', default=False)
    parser.add_argument(dest='paths_database', type=path)
    parser.add_argument(dest='route_database', type=path)
    parser.add_argument(dest='architecture', type=path)
    parser.add_argument(dest='vpr_net_file_namebase')
    parser.add_argument(dest='clbs_per_pin_factor', type=float)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    do_route(str(args.route_database), str(args.paths_database),
             args.vpr_net_file_namebase, args.architecture,
             args.clbs_per_pin_factor, fast=args.fast)