r'''
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
from collections import OrderedDict
import numpy as np
import pandas as pd


def min_success_data(routing_data_frame):
    '''
    To evaluate the "routability" of a placement, it is useful to determine the
    minimum channel-width that the router was able to successfully use to route
    the placement.  In this method we use the `pandas.pivot_table` to extract
    this data from our routing-results data-frame.

    __NB__ `routing_data_frame` is a `DataFrame` instance, containing all rows
    from a HDF `route_states` table.

    See also: `max_failed_data`
    '''
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
    '''
    Determine the _maximum_ channel-width that the router was _unable_ to
    route with for each placement in the route-states data-frame.

    See also: `min_success_data`
    '''

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
    Find missing routing attempts
    =============================

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


def flatten_dict_to_dataframe(data_frames_by_label, label_name='label'):
    '''
    Given a dictionary-like container containing `pandas.DataFrame` instances,
    join all data-frames together into a single data-frame, prepended with an
    additional column containing the dictionary key corresponding to the
    dictionary key each row originated from.

    For example:

    >>> data_frames_by_label = {'A': pd.DataFrame({'a': range(3), 'b': range(3, 6), 'c': range(6, 9)}),
                                'B': pd.DataFrame({'a': range(3), 'b': range(3, 6), 'c': range(6, 9)})}
    >>> for k, v in data_frames_by_label.iteritems():
        print '# %s #' % k
        print v
        print '-' * 15
    ...
    # A #
       a  b  c
    0  0  3  6
    1  1  4  7
    2  2  5  8
    ---------------
    # B #
       a  b  c
    0  0  3  6
    1  1  4  7
    2  2  5  8
    ---------------
    >>> flatten_dict_to_dataframe(data_frames_by_label)
      label  a  b  c
    0     A  0  3  6
    1     A  1  4  7
    2     A  2  5  8
    3     B  0  3  6
    4     B  1  4  7
    5     B  2  5  8
    '''
    label_len = max([len(k) for k in data_frames_by_label.keys()])
    data_array = np.array([(label, ) + tuple(d)
                           for label, df in data_frames_by_label
                           .iteritems()
                           for field, d in df.iterrows()],
                          dtype=zip([label_name, ]
                                    + list(df.keys()),
                                    ('S%d' % label_len, )
                                    + tuple(df.dtypes)))
    return pd.DataFrame(data_array)


def get_flattened_route_states(h5fs, label_name='label'):
    '''
    Generate flattened annealer results table, so we can apply
    pandas manipulation.  The flattened table is in the form:

        |    label   | namebase |  critical_path_delay  |  ...  |   width_fac  |
        |------------|----------|-----------------------|-------|--------------|
        |  vpr-fast  |   alu4   |       117.121n        |  ...  |       11     |
        |  vpr-fast  |   alu4   |       118.630n        |  ...  |       11     |
    '''
    data_frames = OrderedDict([(label,
                        OrderedDict([(net_file_group._v_name,
                                       get_routing_data_frame(
                                        net_file_group.route_states))
                                     for net_file_group in h5f.root]))
                       for label, h5f in h5fs.iteritems()])

    data = OrderedDict([(label,
                        OrderedDict([(net_file_group._v_name,
                                      min_success_data(data_frames
                                                       [label]
                                                       [net_file_group
                                                        ._v_name]))
                                     for net_file_group in h5f.root]))
                       for label, h5f in h5fs.iteritems()])

    flattened_results = flatten_dict_to_dataframe(OrderedDict([
            (k, flatten_dict_to_dataframe(v, 'namebase'))
            for k, v in data.iteritems()]), label_name)
    return flattened_results


def get_max_min_channel_widths(h5fs):
    '''
    There are several issues that may arise when attempting to compare routed
    attributes, such as _critical-path-delay_, across multiple trials of a
    placer configuration.  These issues are even more prevalent when comparing
    results of trials run using several different placement algorithms.  One
    important issue is that the minimum channel-width that leads to a
    successful route may vary among trials for the same placer configuration,
    and especially across trials from several placer algorithms.

    In an attempt to allow a fair comparison in cases of varying
    minimum-channel-width, this function returns the maximum minimum-successful
    channel-width for each net-file, across all algorithms, indexed by
    net-file-namebase.

    In other words, the returned result can be treated like a dictionary, where
    each _key_ is a net-file-namebase, and each _value_ is the maximum
    minimum-successful channel-width for the corresponding net-file.
    '''
    flattened_results = get_flattened_route_states(h5fs)
    max_min_channel_widths = (pd.pivot_table(flattened_results,
                                             values=['width_fac'],
                                             rows=['label',
                                                   'namebase'],
                                             aggfunc=np.max)
                              .transpose().rename(
                                      {'width_fac':
                                       'max_min_channel_widths'}))
    flattened_max_min = pd.melt(max_min_channel_widths)
    return pd.pivot_table(flattened_max_min,
                          values=['value'],
                          cols=['namebase'], aggfunc=np.max)


def get_routing_data_frame(hdf_route_states, dtype=None):
    '''
    Create a `pandas.DataFrame` from the contents of an HDF `route_states`
    table.

    By default, the `dtype` is not set.
    '''
    data = np.array([v.fetch_all_fields()
                     for v in hdf_route_states],
                    dtype=dtype)
    return pd.DataFrame(data)


def get_routing_data_frames(h5fs, channel_widths_by_namebase):
    r'''
    Return a hierarchy of data-frames, indexed by HDF _label_, then by
    _net-file-namebase_, for all routing results matching the routing
    channel-widths specified on a per-net-file basis.

    Overview
    ========

    Given a list of open HDF-5 routing-results files and a set of
    channel-widths indexed by net-file-namebase _(e.g., `ex5p`, `tseng`),
    return a hierarchy of `pandas.DataFrame` instances, which include all
    routing-states results matching the specified
    net-file-namebase/channel-width pairs.  To reiterate, for each namebase,
    only results matching the channel-width from `channel_widths_by_namebase`
    will be included in the data-frames.

    Example
    =======

    Let's consider a case where we have the following
    `channel_widths_by_namebase`:

        channel_widths_by_namebase = {'ex5p': 12, 'tseng': 9, ...}


    The structure of the resulting hierarchy would be:

                      combined      <------- OrderedDict
                       / | \
                      /  |  \
                     /   |   \
                    /    |    \
                   /     |     \
                  /      |      \
                 /       |       \
                /        |        \
           algorithm1   ...     algorithmN     <------- OrderedDict
              /|\                  /|\
             / | \                / | \
            /  |  \     ...      /  |  \
           /   |   \            /   |   \
          /    |    \          /    |    \
        ex5p  ...  tseng     ex5p  ...  tseng  <------- pandas.DataFrame

    where each `ex5p` leaf corresponds to a `pandas.DataFrame` containing all
    route-states results for routing the placement produced by running
    `algorithm1` against the net-file, `ex5p`, where a channel-width of 12 was
    used during routing.  The channel-width of 12 was taken from the
    `channel_widths_by_namebase` look-up.
    '''
    combined = OrderedDict()

    for label, h5f in h5fs.iteritems():
        results = {}
        for net_file_group in h5f.root:
            net_file_nambase = net_file_group._v_name
            hdf_route_states = net_file_group.route_states
            target_width_fac = (channel_widths_by_namebase
                                [net_file_nambase])
            data = get_routing_data_frame(hdf_route_states
                                          .where('(width_fac  == '
                                                 '%d)' %
                                                 target_width_fac),
                                          dtype=hdf_route_states.dtype)
            results[net_file_nambase] = (target_width_fac, data)
        combined[label] = results
    return combined
