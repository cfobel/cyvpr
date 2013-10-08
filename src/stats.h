#ifndef ___STATS__HPP___
#define ___STATS__HPP___

void routing_stats (boolean full_stats, enum e_route_type route_type,
         int num_switch, t_segment_inf *segment_inf, int num_segment,
         float R_minW_nmos, float R_minW_pmos, boolean timing_analysis_enabled,
         float **net_slack, float **net_delay);

void print_wirelen_prob_dist (void);

void print_lambda (void);

void get_num_bends_and_length(std::vector<unsigned int> &bends,
                              std::vector<unsigned int> &wire_lengths,
                              std::vector<unsigned int> &segments);

#endif
