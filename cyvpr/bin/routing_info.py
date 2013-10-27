'''
Find placements without any routing results
'''
from path import path
import tables as ts


def find_route_states_table(h5f_route, block_positions_sha1):
    parent_table = None
    for table in h5f_route.walkNodes(h5f_route.root, 'Table'):
        for row in table.where('block_positions_sha1 == "%s"' %
                               block_positions_sha1):
            parent_table = table
            break
    return parent_table


def placements_without_routings(h5f_placed, h5f_routed):
    no_routings = set()

    for table in h5f_placed.walk_nodes(h5f_placed.root, 'Table'):
        if table._v_name == 'placements':
            for sha1 in table.cols.block_positions_sha1:
                if (find_route_states_table(h5f_routed, sha1)
                    is None):
                    no_routings.add((table._v_pathname, sha1))
    return no_routings


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Report placements that do not have '
                            'any corresponding routings.')

    parser.add_argument(dest='hd5_placement_file', type=path)
    parser.add_argument(dest='hd5_routing_file', type=path)
    args = parser.parse_args()
    return args


def main(hd5_placement_file, hd5_routing_file):
    h5f_placed = ts.open_file(str(hd5_placement_file), 'r')
    h5f_routed = ts.open_file(str(hd5_routing_file), 'r')

    no_routings = placements_without_routings(h5f_placed, h5f_routed)
    print '\n'.join([','.join(v) for v in no_routings])

    for h in (h5f_placed, h5f_routed):
        h.close()


if __name__ == '__main__':
    args = parse_args()
    main(args.hd5_placement_file, args.hd5_routing_file)
