#ifndef ___FORMATTER__HPP___
#define ___FORMATTER__HPP___

#include <sstream>


class Formatter {
    /*
     * __TL;DR__ Use to pass variable values to an exception.
     *
     * This class can be used where a constant string must be available, but
     * variable values must be used, usually requiring manual construction
     * using `sprintf` or a `std::stringstream`.  Instead, one can instantiate
     * an instance of this class on the fly and treat it as a
     * `std::stringstream` that can be implicitly (or explicitly) cast as a
     * constant `std::string`.
     *
     * Adapted from:
     *
     *
     * __NB__ This class is particularly helpful when it is necessary to pass
     *        variable values to an exception.  For example:
     *
     *     ...
     *     // implicitly cast to std::string
     *     throw std::runtime_error(Formatter() << "foo: " << 13 << ", bar" <<
     *                              myData);
     *     // explicitly cast to std::string
     *     throw std::runtime_error(Formatter() << "foo << 13 << ", bar" <<
     *                              myData >> Formatter::to_str);
     *     ...
     */
public:
    Formatter() {}
    ~Formatter() {}

    template <typename Type>
    Formatter & operator << (const Type & value) {
        stream_ << value;
        return *this;
    }

    std::string str() const         { return stream_.str(); }
    operator std::string () const   { return stream_.str(); }

    enum ConvertToString {
        to_str
    };
    std::string operator >> (ConvertToString) { return stream_.str(); }

private:
    std::stringstream stream_;

    Formatter(const Formatter &);
    Formatter & operator = (Formatter &);
};

#endif
