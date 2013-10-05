from libcpp.vector cimport vector


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

    struct RouteResult:
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


cdef extern from "globals.h":
    RouteResult g_route_result
    RouteState g_route_state
    vector[RouteState] g_route_states
