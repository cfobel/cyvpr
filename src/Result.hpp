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
class RouteResult : public StateBase {
public:
    string arch_file_md5;
    string net_file_md5;
    string placed_file_md5;
    std::vector<int> success_channel_widths;
    std::vector<int> failure_channel_widths;

    virtual string label() const { return "RouteResult"; }

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

    virtual std::vector<std::pair<string, string> > fieldname_value_pairs() const {
        std::vector<std::pair<string, string> > f;

        f.push_back(std::make_pair("arch_file_md5",
                                   str_value(this->arch_file_md5)));
        f.push_back(std::make_pair("net_file_md5",
                                   str_value(this->net_file_md5)));
        f.push_back(std::make_pair("placed_file_md5",
                                   str_value(this->placed_file_md5)));
        f.push_back(std::make_pair("best_channel_width",
                                   str_value(this->best_channel_width())));

        return f;
    }
};

#endif  // ___RESULT__HPP___
