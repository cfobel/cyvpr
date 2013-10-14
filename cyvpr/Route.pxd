from libcpp.vector cimport vector
from libcpp.string cimport string

from cyvpr.State cimport cStateBase, StateBase


ctypedef unsigned int uint


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


cdef extern from "time.h":
    struct timespec:
        long int tv_sec
        long int tv_nsec


cdef extern from "State.hpp":
    cdef cppclass RouteState:
        timespec start
        timespec end
        int width_fac
        bint success
        float critical_path_delay
        # Tnodes on critical path.
        int tnodes_on_crit_path
        # Non-global nets on critical path.
        int non_global_nets_on_crit_path
        # Global nets on critical path.
        int global_nets_on_crit_path
        # Total logic delay
        float total_logic_delay
        # Total net delay.
        float total_net_delay
        vector[uint] bends
        vector[uint] wire_lengths
        vector[uint] segments
        s_router_opts router_opts

        string str()
        string csv()
        string csv_summary()
        vector[string] csv_fieldnames()
        string csv_header()
        void set(RouteState other)


cdef extern from "Result.hpp":
    cdef cppclass RouteResult:
        string arch_file_md5
        string net_file_md5
        string placed_file_md5
        vector[int] success_channel_widths
        vector[int] failure_channel_widths

        int best_channel_width()
        void set(RouteResult other)
        string str()
        string csv()
        string csv_summary()
        vector[string] csv_fieldnames()
        string csv_header()


cdef datetime_from_timespec_tuple(timespec t)


cdef class cRouteState(cStateBase):
    cdef RouteState *thisptr
    cdef object _bends
    cdef object _wire_lengths
    cdef object _segments

    cdef inline init(self, RouteState state):
        self.thisptr.set(state)


cdef class cRouteResult(cStateBase):
    cdef RouteResult *thisptr

    cdef inline set(self, RouteResult result):
        self.thisptr.set(result)


cdef class cRouterOpts:
    cdef s_router_opts *thisptr
