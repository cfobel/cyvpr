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

    static std::vector<string> csv_fieldnames() {
        std::vector<string> fieldnames;

        fieldnames.push_back("arch_file_md5");
        fieldnames.push_back("net_file_md5");
        fieldnames.push_back("placed_file_md5");
        fieldnames.push_back("best_channel_width");

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
    }

    int best_channel_width() const {
        size_t success_count = this->success_channel_widths.size();
        if (0 < success_count) {
            return this->success_channel_widths[success_count - 1];
        }
        return -1;
    }

    string csv() const {
        stringstream s;

        s << this->arch_file_md5 << ",";
        s << this->net_file_md5 << ",";
        s << this->placed_file_md5 << ",";
        s << this->best_channel_width();

        return s.str();
    }

    string str() const {
        stringstream s;

        s << "arch_file_md5: " << this->arch_file_md5 << endl;
        s << "net_file_md5: " << this->net_file_md5 << endl;
        s << "placed_file_md5: " << this->placed_file_md5 << endl;
        s << "best_channel_width: " << this->best_channel_width() << endl;

        return s.str();
    }
};

#endif  // ___RESULT__HPP___
