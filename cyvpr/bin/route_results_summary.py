from pprint import pprint
from path_helpers import path


def main():
    route_results_files = sorted(path('../route_results').files('*.dat'))
    results = [r.pickle_load() for r in route_results_files]
    pprint([(p.namebase, [(s.width_fac, s.critical_path_delay, s.success)
                          for s in data['states'] if s.success])
            for p, data in zip(route_results_files, results)])


if __name__ == '__main__':
    main()
