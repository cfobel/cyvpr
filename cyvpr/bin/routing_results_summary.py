from pprint import pformat
import cStringIO as StringIO

from path_helpers import path
import numpy as np
import tables as ts
import pandas as pd
from ..result.routing_pandas import (max_failed_data, min_success_data,
                                     min_success_max_failed_channel_width_diff,
                                     missing_routability_result_configs)


def prefix_lines(obj, prefix):
    return '\n'.join([prefix + s for s in str(obj).splitlines()])


def main(routing_hdf_path, net_file_namebase):
    format_opts = dict(((k, pd.get_option(k)) for k in ('float_format',
                                                        'column_space')))
    # Format floats to:
    #
    #   * Avoid small float values being displayed as zero _(e.g.,
    #     critical-path-delay)_.
    #   * Use engineering postfix to make it easier to compare values
    #     at-a-glance _(e.g., `u` for micro, `n` for nano, etc.)_.
    pd.set_eng_float_format(accuracy=3, use_eng_prefix=True)
    h5f = ts.open_file(str(routing_hdf_path), 'r')

    # In our case, we need to first load the data from our `route_states` table
    # from the HDF file into a `pandas.DataFrame` instance.
    net_file_routings = getattr(h5f.root, net_file_namebase)
    data = np.array([v.fetch_all_fields()
                     for v in net_file_routings.route_states],
                    dtype=net_file_routings.route_states.dtype)
    routing_results = pd.DataFrame(data)
    h5f.close()

    string_io = StringIO.StringIO()
    indent = 4 * ' '

    print >> string_io, '# [%s] Routing results summary #\n' % net_file_namebase
    _min_success_data = min_success_data(routing_results)
    if len(_min_success_data) > 1:
        min_success_summary = _min_success_data.describe()
    elif len(_min_success_data) == 1:
        min_success_summary = _min_success_data.iloc[0]
    print >> string_io, '## Minimum routable channel-width summary ##\n'
    print >> string_io, prefix_lines(min_success_summary, indent)

    print >> string_io, '\n' + 70 * '-' + '\n'

    _max_failed_data = max_failed_data(routing_results)
    if len(_min_success_data) > 1:
    #max_failed_summary = _max_failed_data.describe().astype('i')
        max_failed_summary = _max_failed_data.describe()
    elif len(_min_success_data) == 1:
        max_failed_summary = _max_failed_data.iloc[0]
    print >> string_io, '## Maximum unroutable channel-width summary ##\n'
    print >> string_io, prefix_lines(max_failed_summary, indent)

    incomplete_routing_searches = np.where(
        min_success_max_failed_channel_width_diff(routing_results) != 1)
    if len(incomplete_routing_searches[0]):
        print >> string_io, 'Incomplete routings:'
        print >> string_io, '\n'.join(['  * `%s`' %
                                       pformat(routing_results
                                               ['block_positions_sha1'][i])
                                     for i in incomplete_routing_searches[0]])

    print >> string_io, '\n' + 70 * '-' + '\n'

    print >> string_io, ('## Missing routability result routing configurations'
                         ' ##\n')
    print >> string_io, '\n'.join(['  * `%s`' % pformat(v) for v in
                                   missing_routability_result_configs
                                   (routing_results)])

    print >> string_io, '\n' + 70 * '-' + '\n\n'

    for k, v in format_opts.iteritems():
        if v is not None:
            pd.set_option(k, v)
    return string_io.getvalue(), routing_results


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Display a summary of the routing '
                            'results for a single net-file from a HDF results '
                            'file')
    parser.add_argument('-c', '--csv_channel_width', action='store_true',
                        default=False)
    parser.add_argument(dest='routing_hdf_path', type=path)
    parser.add_argument(nargs='*', dest='net_file_namebase')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    if not args.net_file_namebase:
        h5f = ts.open_file(str(args.routing_hdf_path), 'r')
        args.net_file_namebase = [g._v_name for g in h5f.root]
        h5f.close()
    for net_file_namebase in args.net_file_namebase:
        summary, routing_results = main(args.routing_hdf_path,
                                        net_file_namebase)
        if args.csv_channel_width:
            for result in missing_routability_result_configs(routing_results):
                print ','.join(map(str, result))
        else:
            print summary
