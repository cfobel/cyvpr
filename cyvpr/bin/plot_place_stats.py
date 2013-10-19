import tables as ts
from path import path


def plot_place_stats(plot_ctx, stats_table, stats=None, normalize=True,
                     stat_label_format='%s'):
    '''
    Plot the specified placement statistics to the provide plotting context.
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
    plot_objects = plot_place_stats(plot_ctx, stats_table, stats, normalize,
                                    stat_label_format)
    plot_ctx.title('[%s] %s' % (stats_table.getAttr('net_file_namebase'),
                                stats_table.getAttr('block_positions_sha1')))
    plot_ctx.legend()
    return plot_objects


def main(args):
    import matplotlib.pyplot as plt

    h5f = ts.openFile(args.hdf5_placements_file, mode='r')
    placement_results = getattr(h5f.root, args.net_file_namebase)

    if args.block_positions_sha1 is None:
        # No block-positions SHA1 hash specified, so for now, just select the
        # first available set of placement-stats.
        for x in placement_results.placement_stats:
            stats = x
            break
    else:
        stats = getattr(placement_results.placement_stats, 'P_' +
                        args.block_positions_sha1)
    plt.figure()
    return plot_single_place_stats(plt, stats)


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Plot placement results based on '
                            'net-file namebase')
    parser.add_argument('-b', '--block_positions_sha1')
    parser.add_argument(dest='hdf5_placements_file', type=path)
    parser.add_argument(dest='net_file_namebase', type=path)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    print args
    plot_objects = main(args)
