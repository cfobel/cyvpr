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
from .merge_table_nodes import parse_args, merge_tables


def assess_row(other_table, combined_table, row_index, row_data):
    '''
    Decide if the specified row should be appended to the combined-table.
    '''
    if (other_table._v_name == 'placements' and
        (row_data['block_positions_sha1'] in
         combined_table.cols.block_positions_sha1)):
        # In the combined-table, there is already an entry in the table for the
        # specified `block_positions_sha1`, so return `False` to skip it.
        return False
    elif (other_table._v_parent._v_name == 'placement_stats' and
          other_table._v_name.startswith('P_') and
          len(other_table) <= len(combined_table)):
        # All rows from the placement statistics table have already been copied.
        return False
    return True


if __name__ == '__main__':
    args = parse_args()
    merge_tables(args, assess_row=assess_row)
