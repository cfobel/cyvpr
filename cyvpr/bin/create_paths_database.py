import tables as ts
from path import path


def process_path(paths_table, file_path, update):
    md5 = file_path.read_hexhash('md5')

    row_count = 0
    for row in paths_table.where('md5 == "%s"' % md5):
        # The table already contains an entry for this file.
        print ('The table already contains a file with this MD5: %s' %
               md5)
        if update and not row['path'] == file_path.abspath():
            row['path'] = file_path.abspath()
            row.update()
            print '  \--> updated path to: %s' % row['path']
        row_count += 1

    if row_count == 0:
        row = paths_table.row
        row['md5'] = md5
        row['path'] = file_path.abspath()
        row.append()


def main(paths_database_path, net_file_paths, placement_file_paths,
         update=False):
    local_h5f = ts.openFile(paths_database_path, 'a')

    if hasattr(local_h5f.root, 'placement_paths'):
        placement_paths_table = local_h5f.root.placement_paths
    else:
        placement_paths_table = local_h5f.createTable(local_h5f.root,
                                                'placement_paths',
                                                {'md5': ts.StringCol(32,
                                                                     pos=0),
                                                 'path': ts.StringCol(500)})

    if hasattr(local_h5f.root, 'net_file_paths'):
        net_file_paths_table = local_h5f.root.net_file_paths
    else:
        net_file_paths_table = local_h5f.createTable(local_h5f.root,
                                                'net_file_paths',
                                                {'md5': ts.StringCol(32,
                                                                     pos=0),
                                                 'path': ts.StringCol(500)})

    # Create indexes for columns
    for table in (placement_paths_table, net_file_paths_table):
        for col_name in ('md5', ):
            col = getattr(table.cols, col_name)
            if col.index is None:
                col.createCSIndex()
        for col_name in ('path', ):
            col = getattr(table.cols, col_name)
            if col.index is None:
                col.createIndex()

    for placement_file in placement_file_paths:
        process_path(placement_paths_table, placement_file, update)

    placement_paths_table.flush()

    for net_file in net_file_paths:
        process_path(net_file_paths_table, net_file, update)

    net_file_paths_table.flush()


def parse_args():
    """Parses arguments, returns (options, args)."""
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Register net-file or placement files '
                                        'in local database.')
    parser.add_argument('-u', '--update', action='store_true', default=False)
    parser.add_argument(dest='paths_database', type=path)
    parser.add_argument(nargs='+', dest='paths', type=path)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    net_file_paths = [p for p in args.paths if p.ext == '.net']
    placement_paths = [p for p in args.paths if p.ext == '.out']
    main(args.paths_database, net_file_paths, placement_paths, args.update)
