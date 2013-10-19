r'''
Merge results from several VPR placement HDF files into a single HDF output
file.

The input (and output) HDF file have the following structure:

    <net-file_namebase _(e.g., `ex5p`, `clma`, etc.)_> (Group)
        \--> `placements` (Table)


For example:

              root
            /  |   \
           /   |    \
          /    |     \
         /     |      \
        /      |       \
      ex5p    clma    tseng
       |       ...      |
     placements ...   placements


where `ex5p`, `clma`, `tseng` in the above hierarchy represent groups
containing `placements` tables, which store the block-positions, seed, etc., of
each placement.

__NB__ The program [`vitables`] [1] can be used to browse the output file.

[1]: http://vitables.org
'''
from path import path
import tables as ts


def main(combined_output_path, input_paths):
    # Make a copy of the `input_paths` since we might modify the list.
    h5_paths = input_paths[:]
    if not combined_output_path.isfile():
        # The output-path doesn't exist, so use the first input-file as a base.
        h5_base = h5_paths.pop(0)
        ts.copy_file(str(h5_base), str(combined_output_path))
    h5f = ts.open_file(str(combined_output_path), 'a')

    h5fs = [ts.open_file(str(h), mode='r') for h in h5_paths]

    # Iterate through all input HDF files and append the records from all
    # tables found into the table at the corresponding path in the combined,
    # output-file, provided there is not already an entry in the combined table
    # with the same `block_positions_sha1` value..  If the table doesn't
    # already exist in the output file, copy the entire table from the input
    # HDF file.
    for h in h5fs:
        for n in h.walk_nodes(h.root, 'Table'):
            try:
                table = h5f.get_node(n._v_pathname)
                for other_row in n:
                    row = table.row
                    data = other_row.fetch_all_fields()
                    if (data['block_positions_sha1'] not in
                        table.cols.block_positions_sha1):
                        # This placement does not exist in the table yet.
                        for field in data.dtype.fields:
                            row[field] = data[field]
                        row.append()
                    else:
                        print ('[warning]: skipping duplicate row with '
                               '`block_positions_sha1`=%s'
                               % data['block_positions_sha1'])
                table.flush()
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
                h.copy_node(n, parent, recursive=True)
                table = h5f.get_node(n._v_pathname)
            # Create an index on the `seed` column of the placements table _(if
            # it doesn't already exist)_.
            if table.cols.seed.index is None:
                table.cols.seed.create_csindex(filters=n._v_parent._v_filters)
        h.close()
    h5f.close()


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Merge placement results HDF files.')
    parser.add_argument(dest='merged_output_path', type=path)
    parser.add_argument(nargs='+', dest='input_files', type=path)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    assert(args.merged_output_path not in args.input_files)
    print 'Merging the following files:'
    print '  ' + '\n  '.join(args.input_files)
    main(args.merged_output_path, args.input_files)
    print 'Successfully wrote output to:', args.merged_output_path
