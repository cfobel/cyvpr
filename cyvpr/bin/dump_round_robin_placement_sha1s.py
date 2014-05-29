from pprint import pprint

from path_helpers import path
import tables as ts


def round_robin_placement_rows(h5f):
    placement_rows = sorted([(row.fetch_all_fields(), i)
                              for t in h5f.walkNodes('/', 'Table')
                              for i, row in enumerate(t)
                              if t._v_name == 'placements'])
    return placement_rows


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Merge placement results HDF files.')
    parser.add_argument(dest='placement_tables_hdf_file', type=path)
    args = parser.parse_args()
    return args



if __name__ == '__main__':
    args = parse_args()
    h5f = ts.openFile(str(args.placement_tables_hdf_file), 'r')
    try:
        data = round_robin_placement_rows(h5f)
        print '\n'.join([d[0]['block_positions_sha1'] for d in data])
    finally:
        h5f.close()
