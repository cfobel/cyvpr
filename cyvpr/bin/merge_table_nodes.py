r'''
Merge `Table` nodes from several input HDF files into a single, combined HDF
output file.
'''
from path import path
import tables as ts


def merge_table_nodes(combined_output_path, input_paths, mode='a', overwrite=False):
    '''
    Iterate through all tables in the provided input-files, copying _the
    structure_ of each table to the output file.

    If the output file is to be opened in `'w'` mode and the file exists, throw
    an `IOError` unless `overwrite=True`, in which case, the output file will
    be overwritten.
    '''
    # Ensure we are opening in either _write_ or _append_ mode.
    assert(mode in 'wa')

    # Make a copy of the `input_paths` since we might modify the list.
    h5_paths = input_paths[:]
    if mode == 'w' and combined_output_path.isfile() and not overwrite:
        # The output-path exists, but `overwrite` was not enabled, so raise
        # exception.
        raise IOError, ('Output path `%s` already exists.  Specify '
                        '`overwrite=True` to force overwrite.' %
                        combined_output_path)
    h5f = ts.open_file(str(combined_output_path), mode)

    h5fs = [ts.open_file(str(h), mode='r') for h in h5_paths]

    # Iterate through all input HDF files copy any table found at a path that
    # does not yet exist in the output file to the corresponding path in the
    # output file.
    for h in h5fs:
        for n in h.walk_nodes(h.root, 'Table'):
            try:
                h5f.get_node(n._v_pathname)
            except ts.NoSuchNodeError:
                # The table doesn't exist in the destination file, so copy the
                # entire node from the `other` file.
                try:
                    parent = h5f.get_node(n._v_parent._v_pathname)
                except ts.NoSuchNodeError:
                    # The parent group doesn't exist in the destination file,
                    # so create the parent group.
                    parent = h5f.create_group(n._v_parent._v_parent._v_pathname,
                                              n._v_parent._v_name,
                                              filters=n._v_parent._v_filters,
                                              createparents=True)
                h5f.createTable(parent, n._v_name, description=n.description,
                                filters=n.filters)
        h.close()
    h5f.close()


def append_tables(combined_output_path, input_paths, assess_row=None):
    '''
    __NB__ This function does _not_ append table contents together.  It will
    simply copy the first table matching a path that does not exist in the
    output HDF file into the output file.  Therefore, the contents of tables in
    the output file depend on whether a table with the corresponding path is
    present in more than one input file, and in which order the input files are
    processed.  The intention is to combine this function with the
    `append_tables` function to combine tables from several input files
    together by appending the rows of each table with the same path in the
    output file.
    '''
    # Make a copy of the `input_paths` since we might modify the list.
    h5_paths = input_paths[:]
    h5f = ts.open_file(str(combined_output_path), 'a')

    h5fs = [ts.open_file(str(h), mode='r') for h in h5_paths]

    # Iterate through all input HDF files and append the records from all
    # tables found into the table at the corresponding path in the combined,
    # output-file, provided there is not already an entry in the combined table
    # with the same `block_positions_sha1` value..  If the table doesn't
    # already exist in the output file, skip it.
    for h in h5fs:
        for n in h.walk_nodes(h.root, 'Table'):
            try:
                table = h5f.get_node(n._v_pathname)
            except ts.NoSuchNodeError:
                # The table doesn't exist in the destination file, so skip it.
                print ("[warning]: skipping table at path `%s` since the "
                       "table doesn't exist in the output file." %
                       n._v_pathname)
                continue
            for i, other_row in enumerate(n):
                data = other_row.fetch_all_fields()
                if assess_row is None or assess_row(other_table=n,
                                                    combined_table=table,
                                                    row_index=i,
                                                    row_data=data):
                    # Either no `assess_row` was provided by the user _(i.e.,
                    # accept all rows)_, or the `assess_row` function returned
                    # `True`.  Therefore, append the row to the table in the
                    # output file.
                    row = table.row
                    for field in data.dtype.fields:
                        row[field] = data[field]
                    row.append()
                else:
                    print ('[warning]: skipping `%s` row %d since `assess_row`'
                           ' returned `False`' % (n._v_pathname, i))
            table.flush()
        h.close()
    h5f.close()


def merge_tables(args, assess_row=None):
    '''
    Merge tables according to arguments defined in this script's `parse_args`
    function, along with an optional user-specified `assess_row` function.
    This function allows the main functionality of this script to be
    specialized using custom `assess_row` functions.
    '''
    assert(args.merged_output_path not in args.input_files)
    if args.append:
        mode = 'a'
    else:
        mode = 'w'
    print 'Merging the following files:'
    print '  ' + '\n  '.join(args.input_files)
    merge_table_nodes(args.merged_output_path, args.input_files,
                      mode=mode, overwrite=args.force_overwrite)
    append_tables(args.merged_output_path, args.input_files,
                  assess_row=assess_row)
    print 'Successfully wrote output to:', args.merged_output_path


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Merge placement results HDF files.')
    mutex_args = parser.add_mutually_exclusive_group()
    mutex_args.add_argument('-a', '--append', action='store_true',
                            default=False)
    mutex_args.add_argument('-f', '--force_overwrite', action='store_true',
                            default=False)
    parser.add_argument(dest='merged_output_path', type=path)
    parser.add_argument(nargs='+', dest='input_files', type=path)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    merge_tables(args, assess_row=None)
