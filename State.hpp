#ifndef ___STATE__HPP___
#define ___STATE__HPP___

#include <string>
#include <sstream>
#include <iostream>
#include <vector>
#include <map>
#include "timing.hpp"


using std::string;
using std::stringstream;
using std::cout;
using std::endl;

/*
 * # Result types #
 *
 * Added by Christian Fobel <christian@fobel.net> 2013.
 */
class RouteState {
public:
    bool success;
    timespec start;
    timespec end;
    int width_fac;
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

        fieldnames.push_back("success");
        fieldnames.push_back("start_timestamp");
        fieldnames.push_back("end_timestamp");
        fieldnames.push_back("width_fac");
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

    void set(RouteState const &other) {
        this->success = other.success;
        this->start = other.start;
        this->end = other.end;
        this->width_fac = other.width_fac;
        this->critical_path_delay = other.critical_path_delay;
        this->tnodes_on_crit_path = other.tnodes_on_crit_path;
        this->non_global_nets_on_crit_path = other.non_global_nets_on_crit_path;
        this->global_nets_on_crit_path = other.global_nets_on_crit_path;
        this->total_logic_delay = other.total_logic_delay;
        this->total_net_delay = other.total_net_delay;
    }

    string csv() const {
        double start = this->start.tv_sec + (double)this->start.tv_nsec * 1e-9;
        double end = this->end.tv_sec + (double)this->end.tv_nsec * 1e-9;

        stringstream s;

        s << this->success << ",";
        s << start << ",";
        s << end << ",";
        s << this->width_fac << ",";
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

        double start = this->start.tv_sec + (double)this->start.tv_nsec * 1e-9;
        double end = this->end.tv_sec + (double)this->end.tv_nsec * 1e-9;

        s << "success" << this->success << endl;
        s << "start" << start << endl;
        s << "end" << end << endl;
        s << "critical_path_delay: " << this->critical_path_delay << endl;
        s << "tnodes_on_crit_path: " << this->tnodes_on_crit_path << endl;
        s << "non_global_nets_on_crit_path: " << this->non_global_nets_on_crit_path << endl;
        s << "global_nets_on_crit_path: " << this->global_nets_on_crit_path << endl;
        s << "total_logic_delay: " << this->total_logic_delay << endl;
        s << "total_net_delay: " << this->total_net_delay;

        return s.str();
    }
};

#endif  // ___STATE__HPP___
