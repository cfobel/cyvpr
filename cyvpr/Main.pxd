from libcpp.vector cimport vector
from libcpp.string cimport string


cdef extern from "time.h":
    struct timespec:
        long int tv_sec
        long int tv_nsec


cdef extern from "Main.h":
    int __main__(int argc, char *argv[]) except +


cdef extern from "Result.hpp":
    struct RouteState:
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

    cdef cppclass RouteResult:
        string arch_file_md5
        string net_file_md5
        string placed_file_md5
        vector[int] success_channel_widths
        vector[int] failure_channel_widths
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
        void set(RouteResult other)
        string str()
        string csv()
        vector[string] csv_fieldnames()
        string csv_header()


cdef extern from "globals.h":
    RouteResult g_route_result
    RouteState g_route_state
    vector[RouteState] g_route_states
    vector[string] g_args
