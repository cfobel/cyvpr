from collections import OrderedDict
from datetime import datetime
import warnings

from libcpp.map cimport map
from libcpp.vector cimport vector
from libcpp.string cimport string
from libc.stdlib cimport malloc

from cyvpr.Route cimport RouteState, RouteResult, cRouteResult, cRouteState


ctypedef unsigned int uint


cdef extern from "Main.h":
    int __main__(int argc, char *argv[]) except +
    vector[vector[uint]] extract_block_positions()


cdef extern from "vpr_types.h":
    struct s_router_opts:
        float first_iter_pres_fac
        float initial_pres_fac
        float pres_fac_mult
        float acc_fac
        float bend_cost
        int max_router_iterations
        int bb_factor
        int fixed_channel_width
        float astar_fac
        float max_criticality
        float criticality_exp
        #enum e_router_algorithm router_algorithm
        #enum e_base_cost_type base_cost_type
        #enum e_route_type route_type


cdef extern from "stats.h":
    void get_num_bends_and_length(vector[uint] bends,
                                  vector[uint] wire_lengths,
                                  vector[uint] segments)


cdef extern from "globals.h":
    vector[string] g_args
    RouteResult g_route_result
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
        void init(int argc, char **argv)
        void do_place_and_route() except +
        void do_read_place()
        bint route(int width_fac)
        size_t block_count()
        size_t net_count()
