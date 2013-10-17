#ifndef ___STATE__HPP___
#define ___STATE__HPP___

#include <utility>
#include <string>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <vector>
#include <map>
#include "timing.hpp"
#include "vpr_types.h"


using std::string;
using std::stringstream;
using std::cout;
using std::endl;


template <typename T>
inline string str_value(T value) {
    stringstream s;
    s << value;
    return s.str();
}


class StateBase {
public:
    virtual string label() const = 0;
    virtual std::vector<std::pair<string, string> > fieldname_value_pairs() const = 0;
    virtual string csv_header() const {
        stringstream s;
        std::vector<string> fieldnames = csv_fieldnames();
        s << fieldnames[0];
        for (int i = 1; i < fieldnames.size(); i++) {
            s << "," << fieldnames[i];
        }
        return s.str();
    }

    virtual string csv_summary() const {
        stringstream s;

        s << "# " << label() << " #" << endl
          << csv_header() << endl
          << csv();

        return s.str();
    }

    virtual string str() const {
        std::vector<std::pair<string, string> > field_to_val =
                this->fieldname_value_pairs();
        std::vector<std::pair<string, string> >::const_iterator i =
                field_to_val.begin();

        stringstream s;

        s << "# " << label() << " #" << endl << endl;

        for(; i != field_to_val.end(); i++) {
            s << "    " << i->first << ": " << i->second << endl;
        }

        return s.str();
    }

    virtual std::vector<string> csv_fieldnames() const {
        std::vector<std::pair<string, string> > field_to_val =
                this->fieldname_value_pairs();
        std::vector<std::pair<string, string> >::const_iterator i =
                field_to_val.begin();
        std::vector<string> fieldnames;

        for(; i != field_to_val.end(); i++) {
            fieldnames.push_back(i->first);
        }

        return fieldnames;
    }

    virtual string csv() const {
        std::vector<std::pair<string, string> > field_to_val =
                this->fieldname_value_pairs();
        std::vector<std::pair<string, string> >::const_iterator i =
                field_to_val.begin();
        stringstream s;

        if (i != field_to_val.end()) {
            s << i->second;
            i++;
        }
        for(; i != field_to_val.end(); i++) {
            s << "," << i->second;
        }

        return s.str();
    }
};


/*
 * # Result types #
 *
 * Added by Christian Fobel <christian@fobel.net> 2013.
 */
class RouteState : public StateBase {
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
    s_router_opts router_opts;

    std::vector<unsigned int> bends;
    std::vector<unsigned int> wire_lengths;
    std::vector<unsigned int> segments;

    virtual string label() const { return "RouteState"; }

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
        this->bends = other.bends;
        this->wire_lengths = other.wire_lengths;
        this->segments = other.segments;
        this->router_opts = other.router_opts;
    }

    virtual std::vector<std::pair<string, string> > fieldname_value_pairs() const {
        stringstream s;
        s << std::fixed;

        std::vector<std::pair<string, string> > field_value_pairs;

        double start = this->start.tv_sec + (double)this->start.tv_nsec * 1e-9;
        double end = this->end.tv_sec + (double)this->end.tv_nsec * 1e-9;

        field_value_pairs.push_back(std::make_pair("success", str_value(this->success)));

        s.str("");
        s << std::setprecision(9) << end;
        field_value_pairs.push_back(std::make_pair("start", s.str()));

        s.str("");
        s << std::setprecision(9) << start;
        field_value_pairs.push_back(std::make_pair("end", s.str()));

        field_value_pairs.push_back(std::make_pair("critical_path_delay",
                                    str_value(this->critical_path_delay)));
        field_value_pairs.push_back(std::make_pair("tnodes_on_crit_path",
                                    str_value(this->tnodes_on_crit_path)));
        field_value_pairs.push_back(std::make_pair
                ("non_global_nets_on_crit_path",
                 str_value(this->non_global_nets_on_crit_path)));
        field_value_pairs.push_back(std::make_pair("global_nets_on_crit_path",
                                    str_value(this->
                                              global_nets_on_crit_path)));
        field_value_pairs.push_back(std::make_pair("total_logic_delay",
                                    str_value(this->total_logic_delay)));
        field_value_pairs.push_back(std::make_pair("total_net_delay",
                                    str_value(this->total_net_delay)));

        return field_value_pairs;
    }
};


class PlaceStats : public StateBase {
public:
    timespec start;
    timespec end;

    float temperature;
    double mean_cost;
    double mean_bounding_box_cost;
    double mean_timing_cost;
    double mean_delay_cost;
    float place_delay_value;
    float success_ratio;
    double std_dev;
    float radius_limit;
    float criticality_exponent;
    int total_iteration_count;

    virtual string label() const { return "PlaceStats"; }

    void set(PlaceStats const &other) {
        this->start = other.start;
        this->end = other.end;
        this->temperature = other.temperature;
        this->mean_cost = other.mean_cost;
        this->mean_bounding_box_cost = other.mean_bounding_box_cost;
        this->mean_timing_cost = other.mean_timing_cost;
        this->mean_delay_cost = other.mean_delay_cost;
        this->place_delay_value = other.place_delay_value;
        this->success_ratio = other.success_ratio;
        this->std_dev = other.std_dev;
        this->radius_limit = other.radius_limit;
        this->criticality_exponent = other.criticality_exponent;
        this->total_iteration_count = other.total_iteration_count;
    }

    virtual std::vector<std::pair<string, string> > fieldname_value_pairs() const {
        stringstream s;
        s << std::fixed;

        std::vector<std::pair<string, string> > field_value_pairs;

        double start = this->start.tv_sec + (double)this->start.tv_nsec * 1e-9;
        double end = this->end.tv_sec + (double)this->end.tv_nsec * 1e-9;

        s.str("");
        s << std::setprecision(9) << end;
        field_value_pairs.push_back(std::make_pair("start", s.str()));

        s.str("");
        s << std::setprecision(9) << start;
        field_value_pairs.push_back(std::make_pair("end", s.str()));

        field_value_pairs.push_back(std::make_pair("end", s.str()));

        s.str("");
        s << temperature;
        field_value_pairs.push_back(std::make_pair("temperature", s.str()));

        s.str("");
        s << mean_cost;
        field_value_pairs.push_back(std::make_pair("mean_cost", s.str()));

        s.str("");
        s << mean_bounding_box_cost;
        field_value_pairs.push_back(std::make_pair("mean_bounding_box_cost", s.str()));

        s.str("");
        s << mean_timing_cost;
        field_value_pairs.push_back(std::make_pair("mean_timing_cost", s.str()));

        s.str("");
        s << mean_delay_cost;
        field_value_pairs.push_back(std::make_pair("mean_delay_cost", s.str()));

        s.str("");
        s << place_delay_value;
        field_value_pairs.push_back(std::make_pair("place_delay_value", s.str()));

        s.str("");
        s << success_ratio;
        field_value_pairs.push_back(std::make_pair("success_ratio", s.str()));

        s.str("");
        s << std_dev;
        field_value_pairs.push_back(std::make_pair("std_dev", s.str()));

        s.str("");
        s << radius_limit;
        field_value_pairs.push_back(std::make_pair("radius_limit", s.str()));

        s.str("");
        s << criticality_exponent;
        field_value_pairs.push_back(std::make_pair("criticality_exponent", s.str()));

        s.str("");
        s << total_iteration_count;
        field_value_pairs.push_back(std::make_pair("total_iteration_count", s.str()));

        return field_value_pairs;
    }
};


class PlaceState : public StateBase {
public:
    timespec start;
    timespec end;

    s_placer_opts placer_opts;
    std::vector<PlaceStats> stats;

    virtual string label() const { return "PlaceState"; }

    void set(PlaceState const &other) {
        this->start = other.start;
        this->end = other.end;
        this->placer_opts = other.placer_opts;
        this->stats = other.stats;
    }

    virtual std::vector<std::pair<string, string> > fieldname_value_pairs() const {
        stringstream s;
        s << std::fixed;

        std::vector<std::pair<string, string> > field_value_pairs;

        double start = this->start.tv_sec + (double)this->start.tv_nsec * 1e-9;
        double end = this->end.tv_sec + (double)this->end.tv_nsec * 1e-9;

        s.str("");
        s << std::setprecision(9) << end;
        field_value_pairs.push_back(std::make_pair("start", s.str()));

        s.str("");
        s << std::setprecision(9) << start;
        field_value_pairs.push_back(std::make_pair("end", s.str()));

        return field_value_pairs;
    }
};


#endif  // ___STATE__HPP___
