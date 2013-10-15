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
import hashlib
from path import path
from cyvpr.Main import cMain
from cyvpr.manager.table_layouts import get_PLACEMENT_TABLE_LAYOUT
import tables as ts


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
    block_positions = vpr_main.place(net_path, arch_path, 'placed.out',
                                     seed=seed, fast=fast)
    # Use a hash of the block-positions to name the HDF file.
    block_positions_sha1 = hashlib.sha1(block_positions.data).hexdigest()
    filters = ts.Filters(complib='blosc', complevel=6)
    if output_path is not None:
        output_path = str(output_path)
    else:
        output_file_name = '%s-%s.h5' % (net_path.namebase, block_positions_sha1)
        if output_dir is not None:
            output_path = str(output_dir.joinpath(output_file_name))
        else:
            output_path = output_file_name
    path(output_path).makedirs_p()
    print 'writing output to: %s' % output_path

    h5f = ts.openFile(output_file_name, mode='w', filters=filters)

    net_file_results = h5f.createGroup(h5f.root, net_path.namebase,
                                       title='Placement results for %s VPR '
                                       'with `fast`=%s, `place_algorithm`=%s'
                                       % (net_path.namebase, fast,
                                          place_algorithm))

    placements = h5f.createTable(net_file_results, 'placements',
                                 get_PLACEMENT_TABLE_LAYOUT(vpr_main.block_count),
                                 title='Placements for %s VPR with args: %s' %
                                 (net_path.namebase,
                                  ' '.join(vpr_main.most_recent_args())))
    placements.cols.block_positions_sha1.createIndex()
    row = placements.row
    row['net_file_md5'] = net_path.read_hexhash('md5')
    row['block_positions'] = block_positions
    row['block_positions_sha1'] = block_positions_sha1
    row['seed'] = seed
    row.append()
    placements.flush()
    h5f.close()


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
    place(net_path, arch_path, output_path=args.output_path,
          output_dir=args.output_dir, fast=args.fast,
          place_algorithm=args.place_algorithm, seed=args.seed)
