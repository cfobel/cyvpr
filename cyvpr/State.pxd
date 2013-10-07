from libcpp.vector cimport vector
from libcpp.string cimport string


cdef extern from "State.hpp":
    cdef cppclass StateBase:
        string label()
        string csv()
        vector[string] csv_fieldnames()
        string csv_header()
        string csv_summary()
        string str()


cdef class cStateBase:
    cdef StateBase *baseptr
