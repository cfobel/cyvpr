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

#endif  // ___STATE__HPP___
