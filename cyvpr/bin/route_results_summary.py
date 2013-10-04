from pprint import pprint
from path import path


def main():
    route_results_files = sorted(path('../route_results').files('*.dat'))
    results = [r.pickle_load() for r in route_results_files]
    pprint([(p.namebase, r.critical_path_delay, r.success_channel_widths[-1])
            for p, r in zip(route_results_files, results)])


if __name__ == '__main__':
    main()
