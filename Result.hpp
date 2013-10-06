#ifndef ___RESULT__HPP___
#define ___RESULT__HPP___

#include <iostream>
#include <sstream>
#include <string>
#include "State.hpp"

using std::string;
using std::cout;
using std::endl;
using std::stringstream;

/*
 * # Result types #
 *
 * Added by Christian Fobel <christian@fobel.net> 2013.
 */
class RouteResult {
public:
    string arch_file_md5;
    string net_file_md5;
    string placed_file_md5;
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

    static std::vector<string> csv_fieldnames() {
        std::vector<string> fieldnames;

        fieldnames.push_back("arch_file_md5");
        fieldnames.push_back("net_file_md5");
        fieldnames.push_back("placed_file_md5");
        fieldnames.push_back("critical_path_delay");
        fieldnames.push_back("tnodes_on_crit_path");
        fieldnames.push_back("non_global_nets_on_crit_path");
        fieldnames.push_back("global_nets_on_crit_path");
        fieldnames.push_back("total_logic_delay");
        fieldnames.push_back("total_net_delay");

        return fieldnames;
    }

    static string csv_header() {
        stringstream s;
        std::vector<string> fieldnames = csv_fieldnames();
        s << fieldnames[0];
        for (int i = 1; i < fieldnames.size(); i++) {
            s << "," << fieldnames[i];
        }
        return s.str();
    }

    void set(RouteResult const &other) {
        this->arch_file_md5 = other.arch_file_md5;
        this->net_file_md5 = other.net_file_md5;
        this->placed_file_md5 = other.placed_file_md5;
        this->success_channel_widths = other.success_channel_widths;
        this->failure_channel_widths = other.failure_channel_widths;
        this->critical_path_delay = other.critical_path_delay;
        this->tnodes_on_crit_path = other.tnodes_on_crit_path;
        this->non_global_nets_on_crit_path = other.non_global_nets_on_crit_path;
        this->global_nets_on_crit_path = other.global_nets_on_crit_path;
        this->total_logic_delay = other.total_logic_delay;
        this->total_net_delay = other.total_net_delay;
    }

    string csv() const {
        stringstream s;

        s << this->arch_file_md5 << ",";
        s << this->net_file_md5 << ",";
        s << this->placed_file_md5 << ",";
        s << this->critical_path_delay << ",";
        s << this->tnodes_on_crit_path << ",";
        s << this->non_global_nets_on_crit_path << ",";
        s << this->global_nets_on_crit_path << ",";
        s << this->total_logic_delay << ",";
        s << this->total_net_delay;

        return s.str();
    }

    string str() const {
        stringstream s;

        s << "arch_file_md5: " << this->arch_file_md5 << endl;
        s << "net_file_md5: " << this->net_file_md5 << endl;
        s << "placed_file_md5: " << this->placed_file_md5 << endl;
        s << "critical_path_delay: " << this->critical_path_delay << endl;
        s << "tnodes_on_crit_path: " << this->tnodes_on_crit_path << endl;
        s << "non_global_nets_on_crit_path: " << this->non_global_nets_on_crit_path << endl;
        s << "global_nets_on_crit_path: " << this->global_nets_on_crit_path << endl;
        s << "total_logic_delay: " << this->total_logic_delay << endl;
        s << "total_net_delay: " << this->total_net_delay;

        return s.str();
    }
};

#endif  // ___RESULT__HPP___
