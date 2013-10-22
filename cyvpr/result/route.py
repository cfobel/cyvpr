from collections import OrderedDict
import itertools

import tables as ts


def get_route_result_data(route_states_table, block_positions_sha1, width_fac):
    data = route_states_table
    condition = ('(success == True) & (block_positions_sha1 == "%s") '
                '& (width_fac == %d)' % (block_positions_sha1, width_fac))
    result = [r.fetch_all_fields() for r in data.where(condition)][0]
    return OrderedDict(itertools.izip(result.dtype.names[:11], result))


def min_channel_widths(route_states_table):
    width_fac_data = sorted([(success_row['block_positions_sha1'],
                              success_row['width_fac']) for success_row in
                             itertools.ifilter(lambda x: x['success'],
                                               route_states_table)])
    min_width_facs = {}
    for k, g in itertools.groupby(width_fac_data, lambda x: x[0]):
        min_width_facs[k] = min([v[1] for v in g])
    return min_width_facs


def iter_min_channel_width_results(route_states_table):
    min_width_facs = min_channel_widths(route_states_table)
    return (get_route_result_data(route_states_table, block_positions_sha1,
                                  width_fac) for block_positions_sha1,
            width_fac in min_width_facs.iteritems())


if __name__ == '__main__':
    h5f = ts.open_file('routed-combined.h5', 'r')
    route_states_table = h5f.root.clma.route_states
    data_iter = iter_min_channel_width_results(route_states_table)
