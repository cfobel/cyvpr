import os


def get_includes():
    """
    Return the directory that contains the `cyvpr` Cython *.hpp and *.pxd
    header files.

    Extension modules that need to compile against `cyvpr` should use this
    function to locate the appropriate include directory.

    Notes
    -----
    When using ``distutils``, for example in ``setup.py``.
    ::

        import cyvpr
        ...
        Extension('extension_name', ...
                  include_dirs=[...] + cyvpr.get_includes())
        ...

    """
    import cyvpr
    return [os.path.abspath(os.path.dirname(cyvpr.__file__))]


def get_data_root():
    """
    Return the directory that contains the data _(i.e., architecture, net,
    etc.)_ files to use with `cyvpr`.

        import cyvpr
        ...
        print cyvpr.get_data_root()
        ...

    """
    import cyvpr
    return [os.path.abspath(os.path.join(os.path.dirname(cyvpr.__file__),
                                         'data'))]


def get_net_filepath_by_namebase(namebase):
    from path import path

    filepath = path(get_data_root()[0]).joinpath('mcnc', '%s.net' %
                                                 namebase).realpath()
    assert(filepath.isfile())
    return filepath


def get_parser_by_namebase(namebase):
    from vpr_netfile_parser.VprNetParser import cVprNetFileParser

    return cVprNetFileParser(get_net_filepath_by_namebase(namebase))


def get_netfile_info(namebase):
    p = get_parser_by_namebase(namebase)
    netfile_info = dict([('net_count', len(p.net_labels)),
                         ('block_counts', dict([(k, len(v)) for k, v in
                                                p.block_ids_by_type()
                                                .items()]))])
    netfile_info['io_count'] = sum([v for k, v in
                                    netfile_info['block_counts'].items() if k
                                    in ('.input', '.output')])
    netfile_info['clb_count'] = sum([v for k, v in
                                     netfile_info['block_counts'].items() if k
                                     in ('.clb', )])
    netfile_info['clb_to_io_ratio'] = (float(netfile_info['clb_count']) /
                                       netfile_info['io_count'])
    return netfile_info
