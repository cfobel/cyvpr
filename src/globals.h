#ifndef ___GLOBALS__H___
#define ___GLOBALS__H___

#include <vector>
#include <map>
#include <string>
#include "vpr_types.h"
#include "State.hpp"
#include "Result.hpp"

#ifdef IGNORE_PRINTF

#define my_printf(fmt, ...) (0)

#else

#define my_printf(fmt, ...) printf(fmt, ...)

#endif

extern RouteState g_route_state;
extern RouteResult g_route_result;
extern std::vector<RouteState> g_route_states;
extern std::vector<std::string> g_args;
/* Mapping from file type _(i.e., `net`, `arch`, `placed`, or `routed`)_ to
 * corresponding file-path.
 * __NB__ The `routed` file-path is only present when routing is enabled. */
extern std::map<std::string, std::string> g_filepath;
/* The MD5 hash of each file-path in the `g_filepath` map. */
extern std::map<std::string, std::string> g_file_md5;

/* Netlist to be placed stuff. */
extern int num_nets, num_blocks;
extern int num_p_inputs, num_p_outputs, num_clbs, num_globals;
extern struct s_net *net;
extern struct s_block *block;
extern boolean *is_global;

/* Physical FPGA architecture stuff */
extern int nx, ny, io_rat, pins_per_clb;
extern int **pinloc;
extern int *clb_pin_class;
extern boolean *is_global_clb_pin;
extern struct s_class *class_inf;
extern int num_class;

/* chan_width_x is the x-directed channel; i.e. between rows */
extern int *chan_width_x, *chan_width_y; /* numerical form */
extern struct s_clb **clb;

/* [0..num_nets-1] of linked list start pointers.  Defines the routing.  */
extern struct s_trace **trace_head, **trace_tail;

/* Structures to define the routing architecture of the FPGA.           */
extern int num_rr_nodes;
extern t_rr_node *rr_node;                   /* [0..num_rr_nodes-1]          */
extern int num_rr_indexed_data;
extern t_rr_indexed_data *rr_indexed_data;   /* [0 .. num_rr_indexed_data-1] */
extern int **net_rr_terminals;             /* [0..num_nets-1][0..num_pins-1] */
extern struct s_switch_inf *switch_inf; /* [0..det_routing_arch.num_switch-1] */
extern int **rr_clb_source;              /* [0..num_blocks-1][0..num_class-1] */

#endif // ___GLOBALS__H___
