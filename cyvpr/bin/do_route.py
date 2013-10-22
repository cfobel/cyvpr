import tempfile
import hashlib

from cyvpr.Main import cMain
from cyvpr.Route import unix_time
import tables as ts
from path import path
from cyvpr.manager.table_layouts import get_ROUTE_TABLE_LAYOUT


def route(net_path, arch_path, placement_path, output_path=None,
          output_dir=None, fast=True, clbs_per_pin_factor=None,
          channel_width=None, timing_driven=True, max_router_iterations=None):
    '''
    Perform VPR routing and write result to HDF file with the following
    structure:

        <net-file_namebase _(e.g., `ex5p`, `clma`, etc.)_> (Group)
            \--> `route_states` (Table)

    The intention here is to structure the results such that they can be merged
    together with the results from other routings.
    '''
    net_path = path(net_path)
    arch_path = path(arch_path)
    placement_path = path(placement_path)
    vpr_main = cMain()

    routed_temp_dir = path(tempfile.mkdtemp(prefix='routed-'))
    try:
        routed_path = routed_temp_dir.joinpath('routed.out')

        # We just hard-code `routed.out` as the output path, since we aren't using
        # the output file.  Instead, the routing results and states are returned
        # from the `route` method, as an `OrderedDict` with the keys `result` and
        # `states`.
        route_results = vpr_main.route(net_path, arch_path, placement_path,
                                    routed_path, timing_driven=timing_driven,
                                    fast=fast, route_chan_width=channel_width,
                                    max_router_iterations=max_router_iterations)
    finally:
        routed_temp_dir.rmtree()

    block_positions = vpr_main.extract_block_positions()
    block_positions_sha1 = hashlib.sha1(block_positions.data).hexdigest()

    # Use a hash of the block-positions to name the HDF file.
    filters = ts.Filters(complib='blosc', complevel=6)
    if output_path is not None:
        output_path = str(output_path)
    else:
        output_file_name = 'routed-%s-%s' % (net_path.namebase,
                                             block_positions_sha1)
        if fast:
            output_file_name += '-fast'

        if timing_driven:
            output_file_name += '-timing_driven'
        else:
            output_file_name += '-breadth_first'

        if channel_width:
            output_file_name += '-w%d' % channel_width

        if max_router_iterations:
            output_file_name += '-m%d' % max_router_iterations

        output_file_name += '.h5'

        if output_dir is not None:
            output_path = str(output_dir.joinpath(output_file_name))
        else:
            output_path = output_file_name
    parent_dir = path(output_path).parent
    if parent_dir and not parent_dir.isdir():
        parent_dir.makedirs_p()
    print 'writing output to: %s' % output_path

    h5f = ts.openFile(output_path, mode='w', filters=filters)

    net_file_results = h5f.createGroup(h5f.root, net_path.namebase,
                                       title='Routing results for %s VPR '
                                       'with `fast`=%s, `timing_driven`=%s, '
                                       'with `route_chan_width`=%s, '
                                       '`max_router_iterations`=%s'
                                       % (net_path.namebase, fast,
                                          timing_driven, channel_width,
                                          max_router_iterations))

    # TODO: Finish modifying this function for route _(instead of placement)_.
    route_states = h5f.createTable(net_file_results, 'route_states',
                                   get_ROUTE_TABLE_LAYOUT(vpr_main.net_count),
                                   title='Routings for %s VPR with args: %s' %
                                   (net_path.namebase,
                                    ' '.join(vpr_main.most_recent_args())))
    route_states.setAttr('net_file_namebase', net_path.namebase)

    # Index some columns for fast look-up.
    route_states.cols.block_positions_sha1.createIndex()
    route_states.cols.success.createIndex()
    route_states.cols.width_fac.createCSIndex()

    for i, route_state in enumerate(route_results['states']):
        state_row = route_states.row
        state_row['block_positions_sha1'] = block_positions_sha1
        state_row['success'] = route_state.success
        state_row['width_fac'] = route_state.width_fac
        state_row['critical_path_delay'] = route_state.critical_path_delay
        state_row['total_logic_delay'] = route_state.total_logic_delay
        state_row['total_net_delay'] = route_state.total_net_delay
        state_row['tnodes_on_crit_path'] = route_state.tnodes_on_crit_path
        state_row['non_global_nets_on_crit_path'] = (
                route_state.non_global_nets_on_crit_path)
        state_row['global_nets_on_crit_path'] = (route_state
                                                 .global_nets_on_crit_path)

        # Convert start-date-time to UTC unix timestamp
        state_row['start'] = unix_time(route_state.start)
        state_row['end'] = unix_time(route_state.end)

        state_row['router_options'] = tuple(getattr(route_state.router_opts,
                                                    attr) for attr in
                                            ('max_router_iterations',
                                             'first_iter_pres_fac',
                                             'initial_pres_fac',
                                             'pres_fac_mult', 'acc_fac',
                                             'bend_cost', 'bb_factor',
                                             'astar_fac', 'max_criticality',
                                             'criticality_exp'))

        if len(route_state.bends) > 0:
            state_row['net_data'][0][:] = route_state.bends[:]
            state_row['net_data'][1][:] = route_state.wire_lengths[:]
            state_row['net_data'][2][:] = route_state.segments[:]
        state_row.append()
    route_states.flush()

    h5f.close()
    return route_results


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description="""Run VPR route based on net-file namebase""")

    parser.add_argument('-f', '--fast', action='store_true', default=False)
    parser.add_argument(dest='net_path', type=path)
    parser.add_argument(dest='arch_path', type=path)
    parser.add_argument(dest='placement_path', type=path)
    parser.add_argument('-o', '--output_path', type=path)
    parser.add_argument('-D', '--output_dir', type=path)
    parser.add_argument('-m', '--max_router_iterations', type=int)
    mutex_group1 = parser.add_mutually_exclusive_group()
    mutex_group1.add_argument('-b', '--breadth_first', action='store_true', default=False)
    mutex_group1.add_argument('-t', '--timing_driven', action='store_true', default=True)
    mutex_group2 = parser.add_mutually_exclusive_group()
    mutex_group2.add_argument('-w', '--channel_width', type=int)
    mutex_group2.add_argument('-c', '--clbs_per_pin_factor', type=float)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    route(args.net_path, args.arch_path, args.placement_path,
          output_path=args.output_path, output_dir=args.output_dir,
          fast=args.fast, clbs_per_pin_factor=args.clbs_per_pin_factor,
          channel_width=args.channel_width,
          timing_driven=(not args.breadth_first),
          max_router_iterations=args.max_router_iterations)
