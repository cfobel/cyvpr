r'''
Perform VPR placement and write result to HDF file with the following
structure:

    <net-file_namebase _(e.g., `ex5p`, `clma`, etc.)_> (Group)
        \--> `placements` (Table)


For example:

              root
                |
                |
                |
                |
                |
               clma
                |
              placements


where `clma` in the above hierarchy represents a group containing a
`placements` table, which stores the block-positions, seed, etc., of each
placement.  The intention here is to structure the results such that they can
be merged together with the results from other placements.

__NB__ The program [`vitables`] [1] can be used to browse the output file.

[1]: http://vitables.org
'''
import sys
import tempfile
import hashlib
from path import path
from cyvpr.Main import cMain
from cyvpr.manager.table_layouts import (get_PLACEMENT_TABLE_LAYOUT,
                                         get_VPR_PLACEMENT_STATS_TABLE_LAYOUT)
from cyvpr.Route import unix_time
import tables as ts
from vpr_netfile_parser.VprNetParser import cVprNetFileParser


def vpr_placed_lines(vpr_net_path, block_positions, extents=None):
    parser = cVprNetFileParser(vpr_net_path)
    header = '''\
Netlist file: %(vpr_net_path)s   Architecture file: /var/benchmarks/4lut_sanitized.arch
Array size: %(extent_x)d x %(extent_y)d logic blocks

#block name	x	y	subblk	block number
#----------	--	--	------	------------'''
    clb_positions = block_positions[parser.block_ids_by_type()['.clb']]
    if extents is None:
        extents = tuple(clb_positions[:, :2].max(axis=0) -
                        clb_positions[:, :2].min(axis=0))
    else:
        extents = tuple(extents)
    yield header % {'vpr_net_path': vpr_net_path, 'extent_x': extents[0],
                    'extent_y': extents[1], }
    for i, (label, slot_position) in enumerate(zip(parser.block_labels,
                                                   block_positions)):
        yield '%s\t%d\t%d\t%d\t#%d' % (label, slot_position[0],
                                       slot_position[1], slot_position[2], i)


def write_vpr_placed_output(vpr_net_path, block_positions, out=sys.stdout, extents=None):
    for line in vpr_placed_lines(vpr_net_path, block_positions,
                                 extents=extents):
        print >> out, line


def create_placement_file(vpr_net_path, block_positions, extents=None,
                          suffix='', prefix='tmp', dir=None):
    output_dir = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    output_path = path(output_dir).joinpath('placed.out')
    with open(output_path, 'wb') as output_file:
        write_vpr_placed_output(vpr_net_path, block_positions, output_file,
                                extents)
    return output_path


def place(net_path, arch_path, output_path=None, output_dir=None,
          place_algorithm='bounding_box', fast=True, seed=0):
    '''
    Perform VPR placement and write result to HDF file with the following
    structure:

        <net-file_namebase _(e.g., `ex5p`, `clma`, etc.)_> (Group)
            \--> `placements` (Table)

    The intention here is to structure the results such that they can be merged
    together with the results from other placements.
    '''
    vpr_main = cMain()
    # We just hard-code `placed.out` as the output path, since we aren't using
    # the output file.  Instead, the block-positions are returned from the
    # `place` method.
    place_state, block_positions = vpr_main.place(net_path, arch_path,
                                                  'placed.out', seed=seed,
                                                  fast=fast)
    # Use a hash of the block-positions to name the HDF file.
    block_positions_sha1 = hashlib.sha1(block_positions
                                        .astype('uint32').data).hexdigest()
    filters = ts.Filters(complib='blosc', complevel=6)
    if output_path is not None:
        output_path = str(output_path)
    else:
        output_file_name = 'placed-%s-s%d-%s.h5' % (net_path.namebase, seed,
                                                    block_positions_sha1)
        if output_dir is not None:
            output_path = str(output_dir.joinpath(output_file_name))
        else:
            output_path = output_file_name
    parent_dir = path(output_path).parent
    if parent_dir and not parent_dir.isdir():
        parent_dir.makedirs_p()
    print 'writing output to: %s' % output_path

    h5f = ts.openFile(output_file_name, mode='w', filters=filters)

    net_file_results = h5f.createGroup(h5f.root, net_path.namebase,
                                       title='Placement results for %s VPR '
                                       'with `fast`=%s, `place_algorithm`=%s'
                                       % (net_path.namebase, fast,
                                          place_algorithm))

    placements = h5f.createTable(net_file_results, 'placements',
                                 get_PLACEMENT_TABLE_LAYOUT(vpr_main
                                                            .block_count),
                                 title='Placements for %s VPR with args: %s' %
                                 (net_path.namebase,
                                  ' '.join(vpr_main.most_recent_args())))
    placements.setAttr('net_file_namebase', net_path.namebase)

    placements.cols.block_positions_sha1.createIndex()
    row = placements.row
    row['net_file_md5'] = net_path.read_hexhash('md5')
    row['block_positions'] = block_positions
    row['block_positions_sha1'] = block_positions_sha1
    row['seed'] = seed
    # Convert start-date-time to UTC unix timestamp
    row['start'] = unix_time(place_state.start)
    row['end'] = unix_time(place_state.end)

    placer_opts = place_state.placer_opts
    row['placer_options'] = (placer_opts.timing_tradeoff,
                             placer_opts.block_dist,
                             placer_opts.place_cost_exp,
                             placer_opts.place_chan_width,
                             placer_opts.num_regions,
                             placer_opts.recompute_crit_iter,
                             placer_opts.enable_timing_computations,
                             placer_opts.inner_loop_recompute_divider,
                             placer_opts.td_place_exp_first,
                             placer_opts.td_place_exp_last,
                             placer_opts.place_cost_type,
                             placer_opts.place_algorithm)
    row.append()
    placements.flush()

    stats_group = h5f.createGroup(net_file_results, 'placement_stats',
                                  title='Placement statistics for each '
                                  'outer-loop iteration of a VPR anneal for '
                                  '%s with args: %s' %
                                   (net_path.namebase,
                                    ' '.join(vpr_main.most_recent_args())))

    # Prefix `block_positions_sha1` with `P_` to ensure the table-name is
    # compatible with Python natural-naming.  This is necessary since SHA1
    # hashes may start with a number, in which case the name would not be a
    # valid Python attribute name.
    placement_stats = h5f.createTable(stats_group, 'P_' + block_positions_sha1,
                                      get_VPR_PLACEMENT_STATS_TABLE_LAYOUT(),
                                      title='Placement statistics for each '
                                      'outer-loop iteration of a VPR anneal '
                                      'for %s with args: `%s`, which produced '
                                      'the block-positions with SHA1 hash `%s`'
                                      % (net_path.namebase,
                                         ' '.join(vpr_main.most_recent_args()),
                                         block_positions_sha1))
    placement_stats.setAttr('net_file_namebase', net_path.namebase)
    placement_stats.setAttr('block_positions_sha1', block_positions_sha1)

    for stats in place_state.stats:
        stats_row = placement_stats.row
        for field in ('temperature', 'mean_cost', 'mean_bounding_box_cost',
                      'mean_timing_cost', 'mean_delay_cost',
                      'place_delay_value', 'success_ratio', 'std_dev',
                      'radius_limit', 'criticality_exponent',
                      'total_iteration_count', ):
            stats_row[field] = getattr(stats, field)
            stats_row['start'] = (stats.start['tv_sec'] +
                                  stats.start['tv_nsec'] * 1e-9)
            stats_row['end'] = (stats.end['tv_sec'] + stats.end['tv_nsec'] *
                                1e-9)
        stats_row.append()
    placement_stats.flush()

    h5f.close()
    return place_state


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser

    place_algorithms = ('bounding_box', 'net_timing_driven',
                        'path_timing_driven')

    parser = ArgumentParser(description="""Run VPR place based on net-file namebase""")
    mutex_group = parser.add_mutually_exclusive_group()
    mutex_group.add_argument('-o', '--output_path', default=None, type=path)
    mutex_group.add_argument('-d', '--output_dir', default=None, type=path)
    parser.add_argument('-f', '--fast', action='store_true', default=False)
    parser.add_argument('-s', '--seed', default=0, type=int)
    parser.add_argument('-p', '--place_algorithm', choices=place_algorithms,
                        default='bounding_box')
    parser.add_argument(dest='vpr_net_file', type=path)
    parser.add_argument(dest='architecture_file', type=path)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    print args
    net_path = args.vpr_net_file
    arch_path = args.architecture_file
    place_state = place(net_path, arch_path, output_path=args.output_path,
                        output_dir=args.output_dir, fast=args.fast,
                        place_algorithm=args.place_algorithm, seed=args.seed)
