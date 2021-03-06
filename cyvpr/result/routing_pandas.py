'''
# Overview #

Recall that routing results are stored in an HDF file with the following
structure:

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

For more details, see `notebooks/Routing results.ipynb`.
'''
from pprint import pprint

import tables as ts
import numpy as np
import pandas as pd


def min_success_data(routing_data_frame):
    # At this point, `routing_data_frame` is a `DataFrame` instance, containing all
    # rows from the `h5f.root.tseng.route_states` HDF table.

    # To evaluate the "routability" of a placement, it is useful to determine the
    # minimum channel-width that the router was able to successfully use to route
    # the placement.  We can use the `pandas.pivot_table` to extract this data from
    # our routing-results data-frame, as shown below.

    # Pivot data-frame such that each row is indexed by the _(unique)_
    # block-positions-SHA1 for a placement, and the columns
    # of each row contain the values corresponding to the successful
    # routing with the minimum channel-width for the corresponding
    # placement.
    successful = routing_data_frame[routing_data_frame['success'] == True]
    data = pd.pivot_table(successful, values=['width_fac',
                                              'critical_path_delay',
                                              'total_net_delay',
                                              'total_logic_delay'],
                          rows=['block_positions_sha1'], aggfunc=np.min)
    return data


def max_failed_data(routing_data_frame):
    # Repeat, but for the _unsuccessful_ routing with the maximum
    # channel-width for each placement.

    # Pivot data-frame such that each row is indexed by the _(unique)_
    # block-positions-SHA1 for a placement, and the columns
    # of each row contain the values corresponding to the failed
    # routing with the maximum channel-width for the corresponding
    # placement.
    failed = routing_data_frame[routing_data_frame['success'] == False]
    data = pd.pivot_table(failed, values=['width_fac'],
                          rows=['block_positions_sha1'], aggfunc=np.max)
    return data


def min_success_max_failed_channel_width_diff(routing_data_frame):
    '''
    For each placement in the routing-states data-frame, return the difference
    of the minimum successful routing channel-width and the maximum failed
    routing channel-width.

    If all routing binary-searches were successful, there should be a difference
    of _exactly one_ between the minimum successful channel-width and the maximum
    failed channel-width. Otherwise, at least one of the values _(i.e., minimum
    successful or maximum failed)_ must be incorrect.

    Here, we calculate the difference between the minimum successful
    channel-width and the maximum failed channel-width, which makes it
    possible to verify that it is exactly one for all placements.
    '''
    _min_success_data = min_success_data(routing_data_frame)
    _max_failed_data = max_failed_data(routing_data_frame)
    return (_min_success_data['width_fac'] - _max_failed_data['width_fac'])


def missing_routability_result_configs(routing_data_frame):
    '''
    # Find missing routing attempts #

    Since there are routing objectives other than channel-width, it is useful to
    route most _(if not all)_ placements using the same channel-width to allow
    comparison of other resultant routing properties, such as
    _critical-path-delay_.  To do so, it would be nice to attempt to route every
    placement for all channel-widths where at least one placement can be
    successfully routed, but at least one placement fails to route.  Once the
    highest such channel-width is found, all placements should be routed at a
    channel-width of one higher, such that there is at least one channel-width
    for which we have a successful routing for all placements.

    __NB__ As alluded to in the VPR source code, it is possible _(but unlikely)_
    for a placement to successfully route using one channel-width, but be unable
    to route using a particular higher channel-width due to fluke behaviour in
    the routing algorithm.  For now, we'll assume this won't happen until it
    presents itself as an issue.

    Since the VPR router performs a binary search to find the minimum
    channel-width required to successfully route each placement, it is possible
    that many of the routings that we would like perform have already been done.
    Therefore, this function can be used to query which routing tasks still need
    to be performed to retrieve the results for the channel-widths described
    above.

    To do so, we:

      * Find the minimum and maximum channel-width values that were the minimum
        required channel-widths to successfully route each placement.
      * Construct a pivot table, indexed by placement SHA1 hash, where each
        column indicates whether or not the routing corresponding to the column's
        channel-width value was successful.  In the case where no result is
        available for a placement/channel-width combination, a value of `NaN` is
        used.
      * Find all routing configurations where the corresponding result is set to
        `NaN`.  All such routing configurations do not have results, and thus,
        can assumed to be "missing".
      * Return a list of placement-SHA1/channel-width pairs for the routings that
        still need to be performed.
    '''
    _min_success_data = min_success_data(routing_data_frame)

    c_min = _min_success_data['width_fac'].min()
    c_max = _min_success_data['width_fac'].max()
    data = routing_data_frame[(routing_data_frame['width_fac'] >= c_min) &
                              (routing_data_frame['width_fac'] <= c_max)]
    completed_test = data.pivot(index='block_positions_sha1',
                                columns='width_fac', values='success')
    missing_indices = np.where(completed_test != completed_test)
    return [(completed_test.index[i[0]], completed_test.columns[i[1]])
            for i in zip(*missing_indices)]
