#ifndef ___STATE__HPP___
#define ___STATE__HPP___

#include <vector>
#include <map>
#include "timing.hpp"

/*
 * # Result types #
 *
 * Added by Christian Fobel <christian@fobel.net> 2013.
 */
struct RouteState {
    timespec start;
    timespec end;
    int width_fac;
    bool success;
    float critical_path_delay;
    /* Tnodes on critical path. */
    int tnodes_on_crit_path;
    /* Non-global nets on critical path. */
    int non_global_nets_on_crit_path;
    /* Global nets on crit. path. */
    int global_nets_on_crit_path;
    /* Total logic delay */
    float total_logic_delay;
    /* Total net delay. */
    float total_net_delay;
};

#endif  // ___STATE__HPP___
