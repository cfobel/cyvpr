#ifndef ___MAIN__H___
#define ___MAIN__H___

#include <map>
#include <string>
#include <vector>
#include "../vpr_types.h"
#include "../Buffer.hpp"

int __main__ (int argc, char *argv[]);
std::vector<std::vector<unsigned int> > extract_block_positions();


class Main {
protected:
    void attach_signals();
    void reset_buffer();
    void extract_arg_strings();
public:
    int argc_;
    char **argv_;
    enum e_operation operation_;
    struct s_placer_opts placer_opts_;
    struct s_router_opts router_opts_;
    struct s_annealing_sched annealing_sched_;
    struct s_det_routing_arch det_routing_arch_;
    boolean full_stats_;
    boolean verify_binary_search_;
    t_segment_inf *segment_inf_;
    t_timing_inf timing_inf_;
    t_subblock_data subblock_data_;
    t_chan_width_dist chan_width_dist_;
    float constant_net_delay_;
    char net_file_[BUFSIZE];
    char place_file_[BUFSIZE];
    char arch_file_[BUFSIZE];
    char route_file_[BUFSIZE];
    char pad_loc_file_[BUFSIZE];
    boolean show_graphics_;
    int gr_automode_;
    BufferBase *buffer_;
    /* Mapping from file type _(i.e., `net`, `arch`, `placed`, or `routed`)_ to
    * corresponding file-path.
    * __NB__ The `routed` file-path is only present when routing is enabled. */
    std::map<std::string, std::string> filepath_;
    /* The MD5 hash of each file-path in the `g_filepath` map. */
    std::map<std::string, std::string> file_md5_;

    Main() : buffer_(NULL) {
        attach_signals();
    }
    Main(int argc, char **argv) : argc_(argc), argv_(argv), buffer_(NULL) {
        attach_signals();
    }

    size_t block_count();
    size_t net_count();
    void run_default();
    void timing_analysis();
    void init(int argc, char **argv);
    void init();
    void initialize_graphics();
    void do_place_and_route();
    void do_read_place();
    ~Main();
};

#endif
