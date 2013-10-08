#!/usr/bin/env python
import os
import sys
from distutils.core import setup, Extension

from Cython.Build import cythonize
from path import path

include_dirs = [path('.').abspath(), ]
sys.path += include_dirs

cy_config = dict(include_dirs=include_dirs, language='c++',
                 extra_compile_args=['-O3', '-Wfatal-errors'],
                 libraries=['X11', 'm', 'rt'])
c_files = map(str, path('.').abspath().files('*.c'))
cpp_files = map(str, path('.').abspath().files('*.cpp'))
vpr_ext = Extension('cyvpr.Main',  ['cyvpr/Main.pyx'] + c_files + cpp_files,
                    **cy_config)
cy_exts = [Extension('cyvpr.%s' % v, ['cyvpr/%s.pyx' % v], **cy_config)
           for v in ('State', 'Route')]


setup(name = "cyvpr",
    version = "0.0.1",
    description = "VPR FPGA placement, with on Cython bindings",
    keywords = "fpga placement python cython VPR",
    author = "Christian Fobel",
    url = "https://github.com/cfobel/cyvpr",
    license = "",
    long_description = """""",
    packages = ['cyvpr', ],
    ext_modules=cythonize([vpr_ext] + cy_exts)
)
