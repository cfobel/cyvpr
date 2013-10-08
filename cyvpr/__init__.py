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


def get_architecture_root():
    """
    Return the directory that contains the architecture files to use with
    `cyvpr`.

        import cyvpr
        ...
        print cyvpr.get_architecture_root()
        ...

    """
    import cyvpr
    return [os.path.abspath(os.path.dirname(cyvpr.__file__))]
