r'''
Merge results from several VPR routing HDF files into a single HDF output file.

The input (and output) HDF file have the following structure:

    <net-file_namebase _(e.g., `ex5p`, `clma`, etc.)_> (Group)
        \--> `route_states` (Table)


For example:

                 root
               /  |   \
              /   |    \
             /    |     \
            /     |      \
           /      |       \
         ex5p    clma    tseng
          |       ...      |
    route_states  ...   route_states


where `ex5p`, `clma`, `tseng` in the above hierarchy represent groups
containing `route_states` tables, which store the success/failure state, along
with the routing settings for each routing attempt.  The details include:

  * Channel-width (`width_fac`)
  * Start/end-time
  * Success (`True/False`)

__NB__ The program [`vitables`] [1] can be used to browse the output file.

[1]: http://vitables.org
'''
from .merge_table_nodes import parse_args, merge_tables


def assess_row(other_table, combined_table, row_index, row_data):
    '''
    Decide if the specified row should be appended to the combined-table.
    '''
    if (other_table._v_name == 'route_states' and
        (row_data['block_positions_sha1'] in
         combined_table.cols.block_positions_sha1)):
        # Fetch all route-state rows already in the combined route-states table
        # which match the specified `block_positions_sha1`.
        matches = [row.fetch_all_fields() for row in
                   combined_table.where('block_positions_sha1 == "%s"' %
                                        row_data['block_positions_sha1'])]
        # Only consider existing rows that match the channel-width and
        # router-options of the new route-state being considered for merging.
        #matches = [row for row in matches if ((row_data['width_fac'] ==
                                               #row['width_fac']) and
                                              #(row_data['router_options'] ==
                                               #row['router_options']))]
        match = None
        for row in matches:
            channel_width_match = (row_data['width_fac'] == row['width_fac'])
            router_options_match = (row_data['router_options'] ==
                                    row['router_options'])
            if channel_width_match and router_options_match:
                match = row
                break
            #else:
                #print ('No match:\n    channel_width=%s != %s\n '
                       #'router_options=%s != %s' % (row_data['width_fac'],
                                                    #row['width_fac'],
                                                    #row_data['router_options'],
                                                    #row['router_options']))
        if match is not None:
            # In the combined-table, there is already an entry in the table for
            # the specified `block_positions_sha1` and router-settings so
            # return `False` to skip it.
            return False
    #else:
        #print '[assess_row] other_table._v_name=%s' % other_table._v_name
    return True


if __name__ == '__main__':
    args = parse_args()
    merge_tables(args, assess_row=assess_row)
