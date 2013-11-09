r'''
Recall that placement results are stored in an HDF file with the following
structure:

    <net-file_namebase _(e.g., `ex5p`, `clma`, etc.)_> (Group)
        \--> `placements` (Table)
        \--> `placement_stats` (Group)
                \--> `P_` + <`block_positions_sha1`> (Table)


For example:

                    root
                  /  |   \
                 /   |    \
                /    |     \
               /     |      \
              /      |       \
            ex5p    clma     tseng
           /   \     |       /    \
          /     \   ...     /      \
    placements   \  ... placements  stats
                stats                /|\
                 /|\                 ...
                / | \                ...
               /  |  \
         `P_abc` ... `P_a1b2`

where `ex5p`, `clma`, `tseng` in the above hierarchy represent groups
containing `placements` tables, which store the block-positions and other
details about each placement, along with the SHA1 hash of the 32-bit unsigned
integer block-positions array.  The SHA1 hash is used to uniquely identify a
placement.  The `placement_stats` group contains a table for each placement in
the `placements` table, named according to the SHA1 hash of the corresponding
placement block-positions.  Each `placement_stats` table includes a row for
each outer-loop iteration of the place process.

__NB__ The program [`vitables`] [1] can be used to browse the output file.


To help analyze the placement results from the HDF result files, we use the
[`pandas`] [2] Python package.

From the `pandas` website:

> Python has long been great for data munging and preparation, but less so for
> data analysis and modeling. pandas helps fill this gap, enabling you to carry
> out your entire data analysis workflow in Python without having to switch to
> a more domain specific language like R.


[1]: http://vitables.org
[2]: http://pandas.pydata.org
'''
from pprint import pprint, pformat
import sys

import pandas as pd
import numpy as np
import tables as ts
import scipy.stats
from path import path

from .routing_results_summary import prefix_lines


def engineering_formatted(f):
    def _f(*_args, **_kwargs):
        format_opts = dict(((k, pd.get_option(k)) for k in ('float_format',
                                                            'column_space')))
        # Format floats to:
        #
        #   * Avoid small float values being displayed as zero _(e.g.,
        #     critical-path-delay)_.
        #   * Use engineering postfix to make it easier to compare values
        #     at-a-glance _(e.g., `u` for micro, `n` for nano, etc.)_.
        pd.set_eng_float_format(accuracy=3, use_eng_prefix=True)
        result = f(*_args, **_kwargs)
        for k, v in format_opts.iteritems():
            if v is not None:
                pd.set_option(k, v)
        return result
    return _f


def get_placement_stats_frame(h5f, net_file_namebase):
    net_file_results = getattr(h5f.root, net_file_namebase)
    placement_stats = net_file_results.placement_stats

    # We need to first load the data from our `placement_stats` tables from the HDF
    # file into a `pandas.DataFrame` instance.
    #
    # __NB__ We prepend the placement block-positions SHA1 and the outer-loop
    # iteration index to each row, allowing us to group results by _placement_ or
    # by _outer-loop iteration_.
    data = np.array([(i, table._v_name[2:], )
                    + tuple(row.fetch_all_fields())
                    for table in placement_stats
                    for i, row in enumerate(table)],
                    dtype=[('i', 'u4'), ('sha1', 'S40')]
                    + row.fetch_all_fields().dtype.descr)
    return pd.DataFrame(data)


def cyplace_placement_stats_tables(placement_stats_frame,
                                   stats=('temperature', 'cost',
                                          'radius_limit', 'success_ratio',
                                          'total_move_count')):
    '''
    Call `placement_stats_tables` with default placement-stats fields for a
    cyplace place operation.
    '''
    return placement_stats_tables(placement_stats_frame, stats)


def vpr_placement_stats_tables(placement_stats_frame,
                               stats=('temperature', 'mean_cost',
                                      'radius_limit', 'success_ratio',
                                      'total_iteration_count')):
    '''
    Call `placement_stats_tables` with default placement-stats fields for a VPR
    place operation.
    '''
    return placement_stats_tables(placement_stats_frame, stats)


def placement_stats_tables(placement_stats_frame, stats):
    '''
    Since multiple trials are run for each placer configuration, it is useful
    to summarize the data across all trials to evaluate the performance of the
    corresponding placer configuration.  To do so, we generate
    [pivot-tables][1] using [`pandas.pivot_table`][2].  The pivot-tables allow
    us to compute aggregate summary values for each of several statistics
    _(e.g., temperature)_ at each outer-loop iteration.

    Below, we compute pivot-tables to aggregate the _mean_, _minimum_, _maximum_,
    and _standard-deviation_ of each of the following values at each outer-loop
    iteration, across all trials:

      * Temperature
      * Cost
      * Radius-limit

    [1]: http://en.wikipedia.org/wiki/Pivot_table
    [2]: http://pandas.pydata.org/pandas-docs/stable/reshaping.html
    '''
    # Compute the mean of each stat-of-interest _(i.e., `temperature`,
    # `radius_limit`, etc.)_ across each placement trial, indexed by outer-loop
    # iteration.  Note that the trials combined are from place operations run
    # with all parameters controlled except for the `seed`.
    #
    # __NB__ This stats table provides us with a summary of results based on
    # placing with a specific algorithm with a specific set of parameters, but
    # with varying seed values, providing a sample of results for statistical
    # comparison against other placers and placer configurations.
    stats_tables = {}

    for aggfunc in ('mean', 'min', 'max', 'std'):
        stats_table = pd.pivot_table(placement_stats_frame, values=list(stats),
                                     rows=['i'], aggfunc=getattr(np, aggfunc))
        stats_tables[aggfunc] = stats_table
    return stats_tables


def plot_stats_tables(plot_context, stats_tables, stats, label_prefix='',
                      **kwargs):
    '''
    Given a set of placement-stats pivot-tables, plot the mean values of each
    stat, for each outer-loop iteration, showing the trend of each stat
    throughout the place process.

    __NB__ The error-bars are used to show the range of values _(i.e.,
    _minimum_ to _maximum_)_ across the trials, at each point of the curve
    _(i.e., at each outer-loop iteration)_.
    '''
    for stat in stats:
        mean_data = stats_tables['mean'][stat]
        min_data = stats_tables['min'][stat]
        max_data = stats_tables['max'][stat]
        max_mean = mean_data.max()
        plot_context.errorbar(range(len(mean_data)), mean_data / max_mean,
                              #label='%s%s (%s - %s)' % (label_prefix, stat,
                                                        #mean_data.min(),
                                                        #max_mean),
                              label='%s%s' % (label_prefix, stat),
                              yerr=((mean_data - min_data) / max_mean,
                                    (max_data - mean_data) / max_mean),
                              **kwargs)


def wilcoxon_signed_rank_compare(placement_stats,
                                 test_variables=('runtime', 'mean_cost',
                                                 'success_ratio',
                                                 'total_iteration_count')):
    '''
    Given two `placement_stats` tables corresponding to placer configurations
    `A` and `B`, respectively, perform a [Wilcoxon signed-rank test] [1]
    comparison on final _(i.e., after the last outer-loop iteration)_ stats
    such as:

    * `cost`
    * `temperature`
    * `success_ratio`
    * etc.

    __NB__ From Wikipedia:

    > The Wilcoxon signed-rank test is a non-parametric statistical hypothesis
    > test used when comparing two related samples, matched samples, or
    > repeated measurements on a single sample to assess whether their
    > population mean ranks differ (i.e. it is a paired difference test). It
    > can be used as an alternative to the paired Student's t-test, t-test for
    > matched pairs, or the t-test for dependent samples when the population
    > cannot be assumed to be normally distributed.

    This type of comparison provides a mechanism to determine whether or
    not there is a statistically significant difference in behaviour
    between two placer configurations.

    [1]: http://en.wikipedia.org/wiki/Wilcoxon_signed-rank_test
    '''
    placement_results = {}
    for f, stats in placement_stats.iteritems():
        #                 |<------------->|  -> block_positions_sha1
        data = np.array([(table._v_name[2:],
        #                 |<------   Calculate runtime     ----->|
                          table.cols.end[-1] - table.cols.start[0]) +
                         tuple(table[-1])
                        for table in stats],
                        dtype=[('sha1', 'S40'), ('runtime', 'f8')]
                        + table[0].dtype.descr)
        placement_results[f] = pd.DataFrame(data)
    a, b = placement_results.values()
    p_values_dict = dict([(stat, (scipy.stats.wilcoxon(a[stat], b[stat])[-1],
                                  dict([(label, v[stat].describe())
                                        for label, v in
                                        placement_results.items()])))
                          for stat in test_variables])
    return p_values_dict


def main(h5f_paths, net_file_namebase):
    '''
    Perform Wilcoxon signed-rank test on common final stats from two
    `placement_stats` HDF tables.
    '''
    h5fs = dict([(label, ts.open_file(str(h5f_path)))
                 for label, h5f_path in h5f_paths.iteritems()])

    try:
        net_file_results = dict([(f, getattr(h5f.root, net_file_namebase))
                                for f, h5f in h5fs.iteritems()])
        placement_stats = dict([(f, n.placement_stats)
                                for f, n in net_file_results.iteritems()])

        result = wilcoxon_signed_rank_compare(placement_stats)
    finally:
        for h5f in h5fs.itervalues():
            h5f.close()
    return result


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Display a summary comparison of the '
                            'place results for a single net-file from a pair '
                            'HDF results files.')
    parser.add_argument('-e', '--engineering_formatted', action='store_true',
                        default=False)
    parser.add_argument('-l', '--label', action='append',
                        help='Specify a label for a place-results HDF file.  '
                        'May be specified multiple times, and will match up '
                        'with the respective `place_hdf` path.')
    parser.add_argument(dest='vpr_net_file_namebase')
    parser.add_argument(nargs=2, dest='place_hdf', type=path)
    args = parser.parse_args()
    if args.label is None:
        args.label = [p.namebase for p in args.place_hdf]
    elif len(args.label) > 2:
        parser.print_usage()
        raise SystemExit
    else:
        args.label = args.label + list('AB'[len(args.label):])
    return args


def print_wilcoxon_compare_summary(result, net_file_namebase):
    output = sys.stdout

    print >> output, '# Wilcoxon signed-rank test results #'
    print >> output, '## [%s] `%s` vs `%s` ##' % tuple([net_file_namebase, ] +
                                                       result.values()[0][1]
                                                       .keys())

    for k, v in result.iteritems():
        print >> output, '\n' + 70 * '-' + '\n'
        print >> output, '### `%s` ###\n' % k
        print >> output, '#### _p_-value = %s ####\n' % v[0]

        for label, description in v[1].iteritems():
            print >> output, '#### `%s` ####\n' % label
            print >> output, prefix_lines(pformat(description), 4 * ' ')
            print >> output, '\n' + 70 * '-' + '\n'


if __name__ == '__main__':
    args = parse_args()
    func_args = (dict(zip(args.label, args.place_hdf)),
                 args.vpr_net_file_namebase)
    if args.engineering_formatted:
        func = engineering_formatted(main)
    else:
        func = main
    result = func(*func_args)
    print_wilcoxon_compare_summary(result, args.vpr_net_file_namebase)
