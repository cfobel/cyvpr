from collections import OrderedDict
from datetime import datetime
import warnings

from libcpp.map cimport map
from libcpp.vector cimport vector
from libcpp.string cimport string
from libc.stdlib cimport malloc

from cyvpr.Place cimport PlaceState, cPlaceState
from cyvpr.Route cimport (RouteState, cRouteState, RouteResult, cRouteResult,
                          s_router_opts, cRouterOpts)


ctypedef unsigned int uint


cdef extern from "Main.h":
    int __main__(int argc, char *argv[]) except +
    vector[vector[uint]] extract_block_positions() except +


cdef extern from "stats.h":
    void get_num_bends_and_length(vector[uint] bends,
                                  vector[uint] wire_lengths,
                                  vector[uint] segments) except +


cdef extern from "globals.h":
    vector[string] g_args
    RouteResult g_route_result
    PlaceState g_place_state
    vector[RouteState] g_route_states
    int pins_per_clb


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
    return extract_block_positions()


cdef extern from "Main.h":
    cdef cppclass Main:
        map[string, string] filepath_
        map[string, string] file_md5_
        s_router_opts router_opts_

        Main()
        void init(int argc, char **argv) except +
        void do_place_and_route() except +
        void do_read_place() except +
        bint route(int width_fac) except +
        size_t block_count()
        size_t net_count()
