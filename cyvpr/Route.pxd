from libcpp.vector cimport vector
from libcpp.string cimport string

from cyvpr.State cimport cStateBase, StateBase


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

    cdef inline init(self, RouteState state):
        self.thisptr.set(state)


cdef class cRouteResult(cStateBase):
    cdef RouteResult *thisptr

    cdef inline set(self, RouteResult result):
        self.thisptr.set(result)
