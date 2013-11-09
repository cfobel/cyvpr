import math
from collections import OrderedDict

import tables as ts
from path import path
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


def plot_h5fs(h5fs, net_file_namebase, figures_per_row=1, enable_legend=False,
              figure_kwargs={}, subplot_kwargs={}, **kwargs):
    '''
    Create a plot for each labelled HDF place-results file, showing the trends
    of stats for each of the placement stats tables corresponding to the
    provided net-file-namebase and each of the HDF file.

    See also:  `plot_single_place_stats` and `plot_place_stats`.
    '''
    import matplotlib.pyplot as plt

    figures_per_row = int(figures_per_row)
    stats_tables = {}
    stats_types = {}
    figure = plt.figure(**figure_kwargs)
    row_count = math.ceil(len(h5fs) / float(figures_per_row))
    axes = []

    for i, (label, h5f) in enumerate(h5fs.iteritems()):
        axis = figure.add_subplot(row_count, figures_per_row, i + 1,
                                  **subplot_kwargs)
        axis.set_title('[%s] %s' % (label, net_file_namebase))
        stats_frame = get_placement_stats_frame(h5f,
                                                net_file_namebase)
        if 'mean_cost' in stats_frame:
            # Assume VPR, so use `vpr_placement_stats_tables`
            stats_tables[label] = vpr_placement_stats_tables(
                    stats_frame)
            stats_types[label] = ('temperature', 'mean_cost',
                                  'radius_limit', 'success_ratio')
        else:
            # Assume `cyplace`, so use `cyplace_placement_stats_tables`.
            stats_tables[label] = cyplace_placement_stats_tables(
                    stats_frame)
            stats_types[label] = ('temperature', 'cost',
                                  'radius_limit', 'success_ratio')
        plot_stats_tables(axis, stats_tables[label],
                          stats=stats_types[label], **kwargs)
        iteration_count = len(stats_tables[label].values()[0])
        axes.append((iteration_count, axis))
    max_iterations = max((iteration_count for iteration_count, axis in axes))
    for iteration_count, axis in axes:
        axis.set_xlim(0, max_iterations)
    if enable_legend:
        for iteration_count, axis in axes:
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

        figure_attrs.update(dict(figsize=figsize, dpi=args.dpi))
        for i in xrange(page_count):
            figure = plot_h5fs(OrderedDict(h5fs.items()
                                           [i * figures_per_page:
                                            (i + 1) * figures_per_page]),
                               args.net_file_namebase, args.figures_per_row,
                               enable_legend=args.plot_legend,
                               figure_kwargs=figure_attrs,
                               subplot_kwargs=subplot_attrs,
                               linewidth=args.plot_linewidth,
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
    parser.add_argument(dest='net_file_namebase', type=path)
    parser.add_argument(nargs='+', dest='hdf5_placements_file')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    print args
    figure = main(args)
