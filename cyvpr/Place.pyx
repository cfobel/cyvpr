from collections import OrderedDict
from datetime import datetime
import warnings
import numpy as np

from libcpp.vector cimport vector
from libcpp.string cimport string


PLACE_ALGORITHMS = {BOUNDING_BOX_PLACE: 'BOUNDING_BOX_PLACE',
                    NET_TIMING_DRIVEN_PLACE: 'NET_TIMING_DRIVEN_PLACE',
                    PATH_TIMING_DRIVEN_PLACE: 'PATH_TIMING_DRIVEN_PLACE'}

PLACE_COST_TYPES = {LINEAR_CONG: 'LINEAR_CONG',
                    NONLINEAR_CONG: 'NONLINEAR_CONG'}



def unix_time(datetime_):
    # Convert Python `datetime` instance to unix seconds-since-epoch.
    # Taken from [here] [1].
    #
    # [1]: http://stackoverflow.com/questions/6999726/python-getting-millis-since-epoch-from-datetime/11111177#11111177
    return (datetime_ - datetime.utcfromtimestamp(0)).total_seconds()


cdef datetime_from_timespec_tuple(timespec t):
    cdef double timestamp = t.tv_sec + <double>t.tv_nsec / 1e9
    print '[datetime_from_timespec_tuple] timestamp = %.9f' % timestamp
    return datetime.fromtimestamp(timestamp)


cdef class cPlaceStats:
    def __cinit__(self, size_t data):
        self.thisptr = <PlaceStats *>data

    property start:
        def __get__(self):
            return self.thisptr.start

    property end:
        def __get__(self):
            return self.thisptr.end

    property temperature:
        def __get__(self):
            return self.thisptr.temperature

    property mean_cost:
        def __get__(self):
            return self.thisptr.mean_cost

    property mean_bounding_box_cost:
        def __get__(self):
            return self.thisptr.mean_bounding_box_cost

    property mean_timing_cost:
        def __get__(self):
            return self.thisptr.mean_timing_cost

    property mean_delay_cost:
        def __get__(self):
            return self.thisptr.mean_delay_cost

    property place_delay_value:
        def __get__(self):
            return self.thisptr.place_delay_value

    property success_ratio:
        def __get__(self):
            return self.thisptr.success_ratio

    property std_dev:
        def __get__(self):
            return self.thisptr.std_dev

    property radius_limit:
        def __get__(self):
            return self.thisptr.radius_limit

    property criticality_exponent:
        def __get__(self):
            return self.thisptr.criticality_exponent

    property total_iteration_count:
        def __get__(self):
            return self.thisptr.total_iteration_count


cdef class cPlacerOpts:
    def __cinit__(self, size_t data):
        self.thisptr = <s_placer_opts *>data

    property timing_tradeoff:
        def __get__(self):
            return self.thisptr.timing_tradeoff

    property block_dist:
        def __get__(self):
            return self.thisptr.block_dist

    property place_cost_exp:
        def __get__(self):
            return self.thisptr.place_cost_exp

    property place_chan_width:
        def __get__(self):
            return self.thisptr.place_chan_width

    property num_regions:
        def __get__(self):
            return self.thisptr.num_regions

    property recompute_crit_iter:
        def __get__(self):
            return self.thisptr.recompute_crit_iter

    property enable_timing_computations:
        def __get__(self):
            return self.thisptr.enable_timing_computations

    property inner_loop_recompute_divider:
        def __get__(self):
            return self.thisptr.inner_loop_recompute_divider

    property td_place_exp_first:
        def __get__(self):
            return self.thisptr.td_place_exp_first

    property td_place_exp_last:
        def __get__(self):
            return self.thisptr.td_place_exp_last

    property place_cost_type:
        def __get__(self):
            return self.thisptr.place_cost_type

    property place_algorithm:
        def __get__(self):
            return self.thisptr.place_algorithm


cdef class cPlaceState(cStateBase):
    def __cinit__(self):
        self.thisptr = new PlaceState()
        self.baseptr = <StateBase *>self.thisptr

    def __str__(self):
        return self.thisptr.str()

    def csv_summary(self):
        return self.thisptr.csv_summary()

    property stats:
        def __get__(self):
            cdef int i
            stats = []
            for i in xrange(self.thisptr.stats.size()):
                stats.append(cPlaceStats(<size_t>&self.thisptr.stats[i]))
            return stats

    property placer_opts:
        def __get__(self):
            return cPlacerOpts(<size_t>&self.thisptr.placer_opts)

    property start:
        def __get__(self):
            return datetime_from_timespec_tuple(self.thisptr.start)

        def __set__(self, value):
            timestamp = unix_time(value)
            self.thisptr.start.tv_sec = int(timestamp)
            self.thisptr.start.tv_nsec = ((timestamp -
                                             self.thisptr.start.tv_sec) *
                                            1e9)

    property end:
        def __get__(self):
            return datetime_from_timespec_tuple(self.thisptr.end)

        def __set__(self, value):
            timestamp = unix_time(value)
            self.thisptr.end.tv_sec = int(timestamp)
            self.thisptr.end.tv_nsec = ((timestamp -
                                           self.thisptr.end.tv_sec) * 1e9)

    def __dealloc__(self):
        del self.thisptr
