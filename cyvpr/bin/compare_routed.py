from collections import OrderedDict
import itertools

import tables as ts
import pandas as pd
from scipy.stats import wilcoxon
from path import path

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


def boxplot_route_state_frames(data_frames, net_file_nambase, column):
    import matplotlib.pyplot as plt

    data_vectors = [df[net_file_nambase][1][column][:]
                    for placer, df in data_frames.iteritems()]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    pd.set_eng_float_format(accuracy=3, use_eng_prefix=True)
    #for i in range(3):
        #ax.annotate(str(data_vectors[i].describe()),
                    #xy=((i + 1.2), (data_vectors[i].describe()['75%'] -
                                    #data_vectors[i].describe()['25%'])
                        #/ 8 + data_vectors[i].describe()['25%']))
    #ax2 = fig.add_subplot(122)
    ax.boxplot(data_vectors)
    ax.set_xticklabels(data_frames.keys())
    ax.set_title('[%s] %s' % (net_file_nambase, column.replace('-', ' ')))
    ax.set_ylabel('%s' % column.replace('-', ' '))
    ax.set_xlabel('placer algorithm')
    ax.annotate('', xy=(1.2, data_vectors[0].mean()), xycoords='data',
                xytext=(1.8, data_vectors[1].mean()), textcoords='data',
                arrowprops={'arrowstyle': '<->'})
    #return fig, ax, ax2, data_vectors
    return fig, ax, data_vectors


def significance_comparison(data_frames, net_file_nambase, column):
    data_vectors = [df[net_file_nambase][1][column][:]
                    for placer, df in data_frames.iteritems()]

    # Perform pairwise Wilcoxon sign-rank test on each paired combination of
    # placer algorithms.
    wilcoxon_results = []
    for (k1, v1), (k2, v2) in itertools.combinations(zip(data_frames.keys(),
                                                        data_vectors), 2):
        min_atoms = min(len(v1), len(v2))
        max_atoms = max(len(v1), len(v2))

        # Require at least $N$ elements in each vector, where $N = 5$.
        # TODO: $N$ should likely be configurable...
        N = 5
        if min_atoms < N:
            raise ValueError, ('At least %d elements are required in each '
                               'vector. (%s has %d, %s has %d)' %
                               (N, k1, len(v1), k2, len(v2)))
        if len(v1) > min_atoms:
            print ('[warning] %s has more elements than %s.  Only using first '
                   '%d elements from %s' % (k1, k2, min_atoms, k1))
            v1 = v1[:min_atoms]
        elif len(v2) > min_atoms:
            print ('[warning] %s has more elements than %s.  Only using first '
                   '%d elements from %s' % (k2, k1, min_atoms, k2))
            v2 = v2[:min_atoms]
        p_value = wilcoxon(v1, v2)[-1]
        wilcoxon_results.append((k1, k2, p_value, p_value < 0.05))

    p_values = pd.DataFrame(wilcoxon_results, columns=('A', 'B', 'p-value',
                                                       'significant'))
    return p_values


if __name__ == '__main__':
    args = parse_args()
    data_frames = main(args.results_dir, args.label)
