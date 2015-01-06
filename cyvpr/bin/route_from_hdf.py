'''
`route_from_hdf`

Perform a run of the VPR router on a placement from a HDF placement result
file, as produced by `cyvpr.bin.place.place` along with the SHA1 hash of a set
of block-positions for a placement within the placement HDF file.
'''
from path_helpers import path
import tables as ts
from .place import create_placement_file, create_placement_file_from_frame
from .do_route import route


def vpr_placed_from_h5f(net_file_paths, arch_path, h5f, block_positions_sha1,
                        **kwargs):
    if '/positions' in h5f:
        placement_version = 2
        placement_frame = h5f['/positions'][h5f['/positions']['placement_sha1']
                                            == block_positions_sha1]
        dims = placement_frame[['x', 'y']].max()
        placed_file = create_placement_file_from_frame(net_file_path,
                                                       placement_frame,
                                                       prefix="placed-",
                                                       extents=tuple(dims))
        net_file_namebase = placement_frame.first()['net_file_namebase']
    else:
        placement_version = 1

        matches = []

        # Look for a table of placements containing an entry matching the specified
        # `block_positions_sha1` value.
        for table in h5f.walkNodes(h5f.root, 'Table'):
            if table._v_name == 'placements':
                matches = [m for m in table.readWhere('block_positions_sha1 == '
                                                    '"%s"' %
                                                    block_positions_sha1)]
                if matches:
                    break

        if not matches:
            raise KeyError, ('No placement found with block_positions_sha1="%s"' %
                            block_positions_sha1)

        placement = matches[0]

        # Infer the corresponding net-file namebase from the placement table's
        # parent group-name.
        net_file_namebase = table._v_parent._v_name

        # Write a VPR-compatible placement output file based on the block-positions
        # read from the HDF placements table.  This file is needed to pass into the
        # VPR routing call.
        placed_file = create_placement_file(net_file_path,
                                            placement['block_positions'],
                                            prefix="placed-")
    return net_file_namebase, placed_file


def route_from_hdf(net_file_paths, arch_path, h5f, block_positions_sha1,
                   **kwargs):
    '''
    Given:

      * A list of paths to search for VPR net-files by namebase _(i.e. `ex5p`,
        `clma)_.
      * The path of a VPR v4.3 architecture file.
      * The path of a HDF placement result file, as produced by
        `cyvpr.bin.place.place`.
      * The SHA1 hash of a set of block-positions for a placement within the
        placement HDF file.

    perform a run of the VPR router using the provided parameters.
    '''
    matches = []

    # Look for a table of placements containing an entry matching the specified
    # `block_positions_sha1` value.
    for table in h5f.walkNodes(h5f.root, 'Table'):
        if table._v_name == 'placements':
            matches = [m for m in table.readWhere('block_positions_sha1 == '
                                                  '"%s"' %
                                                  block_positions_sha1)]
            if matches:
                break

    if not matches:
        raise KeyError, ('No placement found with block_positions_sha1="%s"' %
                         block_positions_sha1)

    placement = matches[0]

    # Infer the corresponding net-file namebase from the placement table's
    # parent group-name.
    net_file_namebase = table._v_parent._v_name

    net_file_path = None

    # Search for a VPR net-file matching the inferred net-file namebase.
    for net_file_root in net_file_paths:
        root = path(net_file_root)
        if root.joinpath(net_file_namebase + '.net').isfile():
            net_file_path = root.joinpath(net_file_namebase + '.net').abspath()
            break

    if net_file_path is None:
        raise KeyError, ('No net-file found with name `%s`' %
                         net_file_namebase)

    # Write a VPR-compatible placement output file based on the block-positions
    # read from the HDF placements table.  This file is needed to pass into the
    # VPR routing call.
    placed_file = create_placement_file(net_file_path,
                                        placement['block_positions'],
                                        prefix="placed-")
    try:
        route_results = route(net_file_path, arch_path, placed_file, **kwargs)
    finally:
        # Remove the temporary VPR-compatible placement file we created.
        placed_file.parent.rmtree()
    return route_results


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description="""Run VPR route based on net-file namebase""")

    parser.add_argument('-f', '--fast', action='store_true', default=False)
    parser.add_argument(dest='hd5_placement_file', type=path)
    parser.add_argument(dest='block_positions_sha1')
    parser.add_argument(dest='arch_path', type=path)
    parser.add_argument(nargs='+', dest='net_path', type=path)
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
    h5f = ts.openFile(str(args.hd5_placement_file), 'r')
    route_results = route_from_hdf(args.net_path, args.arch_path, h5f,
                                   args.block_positions_sha1,
                                   output_path=args.output_path,
                                   output_dir=args.output_dir, fast=args.fast,
                                   clbs_per_pin_factor=args.clbs_per_pin_factor,
                                   channel_width=args.channel_width,
                                   timing_driven=(not args.breadth_first),
                                   max_router_iterations=args.max_router_iterations)
