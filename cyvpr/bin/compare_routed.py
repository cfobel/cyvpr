from collections import OrderedDict

import tables as ts
from pyplot_helpers.plot import significance_boxplot
from pandas_helpers.stats import significance_comparison
from path_helpers import path

from cyvpr import get_netfile_info
from cyvpr.result.routing_pandas import (get_max_min_channel_widths,
                                         get_routing_data_frames)


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser

    parser = ArgumentParser(description="""Run VPR place based on net-file namebase""")
    parser.add_argument(dest='results_dir', type=path)
    parser.add_argument(nargs='+', dest='label')
    args = parser.parse_args()
    return args


def main(results_dir, labels):
    h5f_paths = OrderedDict([(label, 'routed-%s.h5' % label)
                             for label in args.label])
    h5fs = OrderedDict([(k, ts.open_file(v, 'r'))
                        for k, v in h5f_paths.iteritems()])
    max_min_channel_widths = get_max_min_channel_widths(h5fs)
    data_frames = get_routing_data_frames(h5fs, max_min_channel_widths)
    return data_frames


def route_data_frames_extract_net_file_namebase_column(data_frames,
                                                       net_file_namebase,
                                                       column):
    '''
    Return an `OrderedDict` object, where the _keys_ are the same as the keys
    of the provided `data_frames` dictionary-like object, and the _value_ for
    each _key_ is a vector of values corresponding to the specified
    `net_file_namebase` and `column` for the respective data-frame.
    '''
    # `data_frames` is a dictionary-like object, where each value is a `tuple`.
    # The _first_ element in each tuple is the _channel-width_ of the routing,
    # while the _second_ element is the routing-results `pandas.DataFrame`.
    #
    # For statistical comparison, we are only concerned with comparing one of
    # the columns from each data-frame, so iterate through and extract the
    # relevant column from each data-frame, labeled using the data-frame
    # tuple's label.
    return OrderedDict([(label, df[net_file_namebase][1][column][:])
                        for label, df in data_frames.iteritems()])


def significance_boxplot_route_state_frames(ax, data_frames, net_file_namebase,
                                            column):
    '''
    Extract the specified column of values corresponding to the specified
    net-file-namebase from each of the provided data-frames, and plot the
    resulting vectors of values in a significance-box-plot for comparison.

    See also: `pyplot_helpers.plot.significance_boxplot`
    '''
    data_vectors_by_label = (
        route_data_frames_extract_net_file_namebase_column(data_frames,
                                                           net_file_namebase,
                                                           column))
    width_fac = data_frames.values()[0][net_file_namebase][0]
    try:
        compare_results = significance_boxplot(ax, data_vectors_by_label)
    except ValueError, e:
        raise ValueError, '%s [width_fac=%d]' % (e, width_fac)

    pretty_column = column.replace('_', ' ')
    netfile_info = get_netfile_info(net_file_namebase)
    ax.set_title('[%s (w:%d b:%d, r:%d)] %s' % (net_file_namebase,
                                                width_fac,
                                                sum(netfile_info['block_counts']
                                                    .values()),
                                                netfile_info['clb_to_io_ratio'],
                                                pretty_column))
    ax.set_ylabel(pretty_column)
    ax.set_xticklabels(data_frames.keys())

    return compare_results


def route_data_frames_significance_comparison(data_frames, net_file_namebase,
                                              column):
    '''
    Extract the specified column of values corresponding to the specified
    net-file-namebase from each of the provided data-frames, and return a
    `panda.DataFrame` containing the results from pair-wise Wilcoxon
    signed-rank comparisons between the resulting vectors of values.

    See also: `pandas_helpers.stats.significance_comparison`
    '''
    return significance_comparison(
        route_data_frames_extract_net_file_namebase_column(data_frames,
                                                           net_file_namebase,
                                                           column))


if __name__ == '__main__':
    args = parse_args()
    data_frames = main(args.results_dir, args.label)
