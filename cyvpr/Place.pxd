from libcpp.vector cimport vector
from libcpp.string cimport string

from cyvpr.State cimport cStateBase, StateBase


ctypedef unsigned int uint


cdef extern from "vpr_types.h":
    enum e_place_algorithm:
        BOUNDING_BOX_PLACE
        NET_TIMING_DRIVEN_PLACE
        PATH_TIMING_DRIVEN_PLACE

    enum place_c_types:
        LINEAR_CONG
        NONLINEAR_CONG

    struct s_placer_opts:
        float timing_tradeoff
        int block_dist
        float place_cost_exp
        int place_chan_width
        int num_regions
        int recompute_crit_iter
        bint enable_timing_computations
        int inner_loop_recompute_divider
        float td_place_exp_first
        float td_place_exp_last
        place_c_types place_cost_type
        e_place_algorithm place_algorithm


cdef extern from "time.h":
    struct timespec:
        long int tv_sec
        long int tv_nsec


cdef extern from "State.hpp":
    cdef cppclass PlaceStats:
        timespec start
        timespec end

        float temperature
        double mean_cost
        double mean_bounding_box_cost
        double mean_timing_cost
        double mean_delay_cost
        float place_delay_value
        float success_ratio
        double std_dev
        float radius_limit
        float criticality_exponent
        int total_iteration_count

    cdef cppclass PlaceState:
        timespec start
        timespec end
        s_placer_opts placer_opts
        vector[PlaceStats] stats

        string str()
        string csv()
        string csv_summary()
        vector[string] csv_fieldnames()
        string csv_header()
        void set(PlaceState other)


cdef datetime_from_timespec_tuple(timespec t)


cdef class cPlaceStats(cStateBase):
    cdef PlaceStats *thisptr


cdef class cPlaceState(cStateBase):
    cdef PlaceState *thisptr

    cdef inline init(self, PlaceState state):
        self.thisptr.set(state)


cdef class cPlacerOpts:
    cdef s_placer_opts *thisptr
