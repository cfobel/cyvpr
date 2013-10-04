import cPickle as pickle
from cyvpr.Main import vpr, vpr_place, vpr_route
from path import path
import re


def main():
    place_results_dir = path('../place_results')
    placed_files = place_results_dir.files('*.out')
    route_results_dir = place_results_dir.parent.joinpath('route_results')

    for p in placed_files:
        route_pathbase = route_results_dir.joinpath(p.namebase.replace('placed',
                                                                    'routed'))
        # Extract VPR net-file path from placed output file.
        net_path = path(re.split(r'\s+', p.lines()[0])[2])

        if not net_path.exists():
            print ('[warning] skipping route for %s, since the net-file %s is not '
                'accessible or does not exist.')
            continue

        route_output_path = route_pathbase + '.out'
        route_result_path = route_pathbase + '.dat'
        print 'routing placement from: %s' % p
        result = vpr_route(net_path, p, route_output_path)
        route_result_path.pickle_dump(result, pickle.HIGHEST_PROTOCOL)
        print '  Wrote route output to: %s' % route_output_path
        print '  Wrote pickled route result to: %s' % route_result_path


if __name__ == '__main__':
    main()
