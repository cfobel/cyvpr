from pprint import pprint

from path import path
import numpy as np
import tables as ts
import pandas as pd
from ..result.routing_pandas import (max_failed_data, min_success_data,
                                     min_success_max_failed_channel_width_diff,
                                     missing_routability_result_configs)


def main(routing_hdf_path, net_file_namebase):
    h5f = ts.open_file(str(routing_hdf_path), 'r')

    # In our case, we need to first load the data from our `route_states` table
    # from the HDF file into a `pandas.DataFrame` instance.
    data = np.array([v.fetch_all_fields()
                     for v in getattr(h5f.root,
                                      net_file_namebase).route_states],
                    dtype=h5f.root.tseng.route_states.dtype)
    routing_results = pd.DataFrame(data)
    h5f.close()

    _min_success_data = min_success_data(routing_results)
    min_success_summary = _min_success_data.describe()
    print '# Minimum routable channel-width summary #\n'
    print min_success_summary

    print '\n' + 70 * '-' + '\n'

    _max_failed_data = max_failed_data(routing_results)
    max_failed_summary = _max_failed_data.describe().astype('i')
    print '# Maximum unroutable channel-width summary #\n'
    print max_failed_summary

    incomplete_routing_searches = np.where(
        min_success_max_failed_channel_width_diff(routing_results) != 1)
    if len(incomplete_routing_searches[0]):
        print 'Incomplete routings:'
        pprint([routing_results['block_positions_sha1'][i] for i in
                                       incomplete_routing_searches[0]])

    print '\n' + 70 * '-' + '\n'

    print '# Missing routability result routing configurations #\n'
    pprint(missing_routability_result_configs(routing_results))
    return routing_results


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Display a summary of the routing '
                            'results for a single net-file from a HDF results '
                            'file')
    parser.add_argument(dest='routing_hdf_path', type=path)
    parser.add_argument(dest='net_file_namebase')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    routing_results = main(args.routing_hdf_path, args.net_file_namebase)
