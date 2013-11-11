import math
from collections import OrderedDict
from itertools import izip

import tables as ts
from path import path
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from pyplot_helpers.arg_parsers import pdf_pages_params_args_parser

from cyvpr.bin.place_results_summary import (
        get_placement_stats_frame, cyplace_placement_stats_tables,
        vpr_placement_stats_tables, plot_stats_tables)


def plot_place_stats(plot_ctx, stats_table, stats=None, normalize=True,
                     stat_label_format='%s'):
    '''
    Plot the trends of all stats from the `stats` argument throughout the
    `cyplace`-anneal process.

    Each curve represents the _mean_ value of each of several trials, which
    only differ by starting `seed` value.  The error bars designate the range
    of each value at the corresponding outer-loop iteration across the trials.
    '''
    cols = stats_table.cols
    if stats is None:
        stats = ['temperature', 'radius_limit', 'mean_cost']
        for stat in stats[:]:
            if not hasattr(cols, stat):
                stats.remove(stat)
    plot_objects = []
    for stat in stats:
        data = getattr(cols, stat)[:]
        if normalize:
            data /= data.max()
        plot_objects.append(plot_ctx.plot(data, label=stat_label_format %
                                          stat))
    return plot_objects


def plot_single_place_stats(plot_ctx, stats_table, stats=None, normalize=True,
                            stat_label_format='%s'):
    '''
    Plot the trends of all stats from the `stats` argument using
    `plot_place_stats` and label the figure with the net-file-namebase and
    block-positions-SHA1 fields extracted from the attributes of `stats_table`.

    See also:  `plot_place_stats`
    '''
    plot_objects = plot_place_stats(plot_ctx, stats_table, stats, normalize,
                                    stat_label_format)
    plot_ctx.title('[%s] %s' % (stats_table.getAttr('net_file_namebase'),
                                stats_table.getAttr('block_positions_sha1')))
    return plot_objects


def place_extract_stats_types_and_tables(h5fs, net_file_namebase):
    '''
    Extract the aggregate placement stats for the specified _net-file-namebase_
    from each of the specified HDF placement-results files, grouped by HDF-file
    label.

    Return two `OrderedDict` objects:

      * `stats_tables_by_label`:
        * Two-level `OrderedDict`:
          * _Keys_ of _first_ level correspond to labels from `h5fs`.
          * _Keys_ of _second_ level are `('mean', 'min', 'max', 'std')`,
            corresponding to the respective aggregation of the underlying
            placement stats.
      * `stats_types_by_label`:
        * _Keys_ correspond to the labels of the placement-stats available for
          the respective HDF file.
          * For VPR results files, the keys include:

              `('temperature', 'mean_cost', 'radius_limit', 'success_ratio')

          * For `cyplace.bin.run_anneal` results files, the keys include:

              `('temperature', 'cost', 'radius_limit', 'success_ratio')
    '''
    stats_tables_by_label = OrderedDict()
    stats_types_by_label = OrderedDict()
    for i, (label, h5f) in enumerate(h5fs.iteritems()):
        stats_frame = get_placement_stats_frame(h5f,
                                                net_file_namebase)
        if 'mean_cost' in stats_frame:
            # Assume VPR, so use `vpr_placement_stats_tables`
            stats_tables_by_label[label] = vpr_placement_stats_tables(
                    stats_frame)
            stats_types_by_label[label] = ('temperature', 'mean_cost',
                                           'radius_limit', 'success_ratio')
        else:
            # Assume `cyplace`, so use `cyplace_placement_stats_tables`.
            stats_tables_by_label[label] = cyplace_placement_stats_tables(
                    stats_frame)
            stats_types_by_label[label] = ('temperature', 'cost',
                                           'radius_limit', 'success_ratio')
    return stats_tables_by_label, stats_types_by_label


def plot_h5fs(h5fs, net_file_namebase, title_format='[%(label)s]',
              figures_per_row=1, enable_legend=False, stat_boxplot_mode=None,
              figure_kwargs={}, subplot_kwargs={}, **kwargs):
    '''
    Create a plot for each labelled HDF place-results file, showing the trends
    of stats for each of the placement stats tables corresponding to the
    provided net-file-namebase and each of the HDF file.

    The `stat_boxplot_mode` _may_ be set to one of `top`, `bottom`, `left`, or
    `right` to plot a box-plot for each place-stat.  See below for positioning
    corresponding to each box-plot mode:

    `top`
    =====
        _____________
        |  |  |  |  |
        | S| T| A| T|
        |__|__|__|__|
        |           |
        |   trends  |
        |___________|

    `bottom`
    ========
        _____________
        |           |
        |   trends  |
        |___________|
        |  |  |  |  |
        | S| T| A| T|
        |__|__|__|__|

    `left`
    ======
        _________________________
        |  |  |  |  |           |
        | S| T| A| T|   trends  |
        |__|__|__|__|___________|

    `right`
    =======
        _________________________
        |           |  |  |  |  |
        |   trends  | S| T| A| T|
        |___________|__|__|__|__|

    See also:  `plot_single_place_stats` and `plot_place_stats`.
    '''
    import matplotlib.pyplot as plt

    figures_per_row = int(figures_per_row)
    stats_tables = {}
    stats_types = {}
    figure = plt.figure(**figure_kwargs)
    row_count = int(math.ceil(len(h5fs) / float(figures_per_row)))

    if stat_boxplot_mode in ('top', 'bottom'):
        row_count *= 2

    axes = []
    if stat_boxplot_mode in ('left', 'right'):
        root_grid = GridSpec(1, 2)
    elif stat_boxplot_mode in ('top', 'bottom'):
        root_grid = GridSpec(2, 1)
    elif stat_boxplot_mode is None:
        root_grid = GridSpec(1, 1)
    else:
        raise ValueError, ('Invalid boxplot mode: %s.  Must be one of: '
                           '`top`, `bottom`, `left`, or `right`.' %
                           stat_boxplot_mode)

    if stat_boxplot_mode in (None, 'right'):
        trend_index = 0
        stat_index = 1
    elif stat_boxplot_mode in ('left', ):
        trend_index = 1
        stat_index = 0
    elif stat_boxplot_mode in ('bottom', ):
        trend_index = 0
        stat_index = 1
    else:
        trend_index = 1
        stat_index = 0
    trend_grid = GridSpecFromSubplotSpec(len(h5fs), 1,
                                         subplot_spec=root_grid[trend_index])
    stats_tables_by_label, stats_types_by_label = (
            place_extract_stats_types_and_tables(h5fs, net_file_namebase))
    for i, ((label, stats_tables), (label2, stats_types)) in enumerate(izip(
            stats_tables_by_label.iteritems(),
            stats_types_by_label.iteritems())):
        assert(label == label2)
        stat_count = len(stats_types)
        trend_axis = figure.add_subplot(trend_grid[i], **subplot_kwargs)
        trend_axis.set_title(title_format % dict(label=label))
        plot_stats_tables(trend_axis, stats_tables, stats=stats_types,
                          **kwargs)
        stat_boxplot_grid = GridSpecFromSubplotSpec(len(h5fs), stat_count,
                                                    subplot_spec=
                                                    root_grid[stat_index])
        if stat_boxplot_mode is not None:
            for j, stat_type in enumerate(stats_types):
                stat_axis = figure.add_subplot(stat_boxplot_grid[i, j])
                stat_axis.boxplot(stats_tables['mean'][stat_type])
                stat_axis.set_xticklabels([stat_type])
        axes.append(trend_axis)
    for axis in axes:
        if enable_legend:
            axis.legend()
    return figure


def main(args):
    if args.figure_font_size is not None:
        import matplotlib

        matplotlib.rcParams.update({'font.size': args.figure_font_size})

    def extract_label_h5f_pair(p):
        p_parts = p.split('::')
        if not p_parts or len(p_parts) > 2:
            raise ValueError, ('H5F path description must have _at most_ one '
                               'occurrence of `::`')
        elif len(p_parts) == 1:
            p_parts.insert(0, path(p_parts[0]).namebase)
        return p_parts[0], path(p_parts[1])
    label_h5f_pairs = map(extract_label_h5f_pair, args.hdf5_placements_file)

    if args.h5f_label_lambda is None:
        h5f_label_lambda = lambda label, p: label
    else:
        h5f_label_lambda = eval('lambda label, p: %s' % args.h5f_label_lambda)

    h5fs = OrderedDict([(h5f_label_lambda(label, p),
                         ts.open_file(str(p), mode='r'))
                        for label, p in label_h5f_pairs])
    figure_attrs = {}
    for attr, value_expr in [a.split(':') for a in args.figure_attr]:
        figure_attrs[attr] = eval(value_expr)
    subplot_attrs = {}
    for attr, value_expr in [a.split(':') for a in args.plot_attr]:
        subplot_attrs[attr] = eval(value_expr)
    try:
        if ((args.figure_width_inches is None) !=
             (args.figure_height_inches is None)):
            raise ValueError, ('If either `figure-width-inches` _or_ '
                               'figure-height-inches` is set, they _both_ must'
                               ' be set.')
        if args.figure_width_inches:
            figsize = (args.figure_width_inches, args.figure_height_inches)
        else:
            figsize = None
        if args.figures_per_page is None:
            page_count = 1
        else:
            page_count = int(math.ceil(len(h5fs) /
                                       float(args.figures_per_page)))
        figures = []
        figures_per_page = int(math.ceil(len(h5fs) / float(page_count)))
        page_count = int(math.ceil(len(h5fs) / float(figures_per_page)))
        print 'page_count:', page_count
        print 'file count:', len(h5fs)
        print 'figures_per_page:', figures_per_page

        if args.plot_linewidth is None:
            linewidth = matplotlib.rcParams.get('lines.linewidth', 1.)
        else:
            linewidth = args.plot_linewidth
        figure_attrs.update(dict(figsize=figsize, dpi=args.dpi))
        for i in xrange(page_count):
            figure = plot_h5fs(OrderedDict(h5fs.items()
                                           [i * figures_per_page:
                                            (i + 1) * figures_per_page]),
                               args.net_file_namebase, args.figures_per_row,
                               stat_boxplot_mode=args.stat_boxplot_mode,
                               enable_legend=args.plot_legend,
                               figure_kwargs=figure_attrs,
                               subplot_kwargs=subplot_attrs,
                               linewidth=linewidth,
                               errorevery=args.error_every)
            figures.append(figure)
        if args.pdf_path is not None:
            from matplotlib.backends.backend_pdf import PdfPages

            pdf_pages = PdfPages(args.pdf_path)
            for figure in figures:
                pdf_pages.savefig(figure)
            pdf_pages.close()
    finally:
        for h5f in h5fs.itervalues():
            h5f.close()
    return figure


def parse_args():
    '''
    Parses arguments, returns (options, args).
    '''
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Plot placement results based on '
                            'net-file namebase',
                            parents=[pdf_pages_params_args_parser()],
                            add_help=False)
    parser.add_argument('-e', '--error-every', type=int, default=5,
                        help='Only show error bars at every `error_every`th '
                        'iteration. (default=%(default)s)')
    parser.add_argument('-b', '--block_positions_sha1')
    parser.add_argument('--h5f-label-lambda', type=str)
    parser.add_argument('--stat-boxplot-mode', choices=('top', 'bottom',
                                                        'left', 'right'))
    parser.add_argument(dest='net_file_namebase', type=path)
    parser.add_argument(nargs='+', dest='hdf5_placements_file')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    print args
    figure = main(args)
