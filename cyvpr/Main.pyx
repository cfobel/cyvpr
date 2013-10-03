from libcpp.vector cimport vector
from libcpp.string cimport string


def vpr():
    cdef char *argv[20]
    cdef vector[string] args

    args.push_back("./vpr")
    argv[0] = <char *>args[0].c_str()
    print __main__(2, argv)
