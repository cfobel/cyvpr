from collections import OrderedDict
from datetime import datetime
import warnings

from libcpp.map cimport map
from libcpp.vector cimport vector
from libcpp.string cimport string
from libc.stdlib cimport malloc


ctypedef unsigned int uint


cdef extern from "Main.h":
    int __main__(int argc, char *argv[]) except +
    vector[vector[uint]] extract_block_positions()


cdef extern from "globals.h":
    vector[string] g_args
    map[string, string] g_filepath
    map[string, string] g_file_md5


cdef inline vpr(args):
    cdef int argc = len(args) + 1
    cdef char **argv = <char **> malloc(argc * sizeof(char *))
    cdef vector[string] args_

    args_.push_back("./vpr")
    for a in args:
        args_.push_back(str(a))

    cdef int i
    for i in xrange(args_.size()):
        argv[i] = <char *>args_[i].c_str()
    __main__(args_.size(), argv)
    data = OrderedDict([
        ('file_md5s', g_file_md5),
        ('filepaths', g_filepath),
        ('block_positions', extract_block_positions()),
    ])
    return data
