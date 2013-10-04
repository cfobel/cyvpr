#ifndef ___RESULT__HPP___
#define ___RESULT__HPP___

#include <vector>
#include <map>

/*
 * # Result types #
 *
 * Added by Christian Fobel <christian@fobel.net> 2013.
 */
struct RouteResult {
    std::vector<int> success_channel_widths;
    std::vector<int> failure_channel_widths;
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
#endif  // ___RESULT__HPP___
