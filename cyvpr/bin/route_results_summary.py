from pprint import pprint
from path import path


def main():
    route_results_files = sorted(path('../route_results').files('*.dat'))
    results = [r.pickle_load() for r in route_results_files]
    pprint([(p.namebase, [(s.width_fac, s.critical_path_delay)
                          for s in states if s.success])
            for p, (r, states) in zip(route_results_files, results)])


if __name__ == '__main__':
    main()
