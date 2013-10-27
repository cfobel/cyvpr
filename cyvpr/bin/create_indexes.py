'''
Create indexes for `block_positions_sha1` and `seed` columns.
'''
from path import path
import tables as ts


def create_indexes(h5f, column_name, cs_index=False):
    for table in h5f.walk_nodes(h5f.root, 'Table'):
        col = getattr(table.cols, column_name, None)
        if col is not None and col.index is None:
            if cs_index:
                print 'creating completely sorted index for: %s.%s' % (table
                                                                       ._v_pathname,
                                                                       column_name)
                col.create_csindex()
            else:
                print 'creating index for: %s.%s' % (table._v_pathname,
                                                     column_name)
                col.create_index()


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Create indexes for all tables with '
                            'the specified column(s).')

    parser.add_argument(dest='h5f_file', type=path)
    parser.add_argument('-i', '--index', action='append')
    parser.add_argument('-c', '--cs_index', action='append')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    if args.index is None and args.cs_index is None:
        raise SystemExit, 'No index columns specified.'
    assert(args.h5f_file.isfile())
    h5f = ts.open_file(str(args.h5f_file), 'a')
    if args.index:
        for index in args.index:
            create_indexes(h5f, index, False)
    if args.cs_index:
        for index in args.cs_index:
            create_indexes(h5f, index, True)
    h5f.close()
