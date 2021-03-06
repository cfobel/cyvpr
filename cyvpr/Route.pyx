from collections import OrderedDict
from datetime import datetime
import warnings
import numpy as np

from libcpp.vector cimport vector
from libcpp.string cimport string
from libc.stdlib cimport malloc

from cyvpr.Place cimport datetime_from_timespec_tuple
from cyvpr.Place import unix_time


def rebuild(data):
    r = cRouteResult()
    for k, v in data.iteritems():
        setattr(r, k, v)
    return r


def rebuild_state(data):
    r = cRouteState()
    for k, v in data.iteritems():
        setattr(r, k, v)
    return r


cdef class cRouterOpts:
    def __cinit__(self, size_t data):
        self.thisptr = <s_router_opts *>data

    property first_iter_pres_fac:
        def __get__(self):
            return self.thisptr.first_iter_pres_fac

    property initial_pres_fac:
        def __get__(self):
            return self.thisptr.initial_pres_fac

    property pres_fac_mult:
        def __get__(self):
            return self.thisptr.pres_fac_mult

    property acc_fac:
        def __get__(self):
            return self.thisptr.acc_fac

    property bend_cost:
        def __get__(self):
            return self.thisptr.bend_cost

    property max_router_iterations:
        def __get__(self):
            return self.thisptr.max_router_iterations

    property bb_factor:
        def __get__(self):
            return self.thisptr.bb_factor

    property fixed_channel_width:
        def __get__(self):
            return self.thisptr.fixed_channel_width

    property astar_fac:
        def __get__(self):
            return self.thisptr.astar_fac

    property max_criticality:
        def __get__(self):
            return self.thisptr.max_criticality

    property criticality_exp:
        def __get__(self):
            return self.thisptr.criticality_exp


cdef class cRouteState(cStateBase):
    def __cinit__(self):
        self.thisptr = new RouteState()
        self.baseptr = <StateBase *>self.thisptr
        self._bends = None
        self._wire_lengths = None
        self._segments = None

    def __reduce__(self):
        start = self.start
        data = OrderedDict([('start', self.start),
                            ('end', self.end),
                            ('success', self.success),
                            ('width_fac', self.width_fac),
                            ('critical_path_delay', self.critical_path_delay),
                            ('tnodes_on_crit_path', self.tnodes_on_crit_path),
                            ('non_global_nets_on_crit_path',
                             self.non_global_nets_on_crit_path),
                            ('global_nets_on_crit_path',
                             self.global_nets_on_crit_path),
                            ('total_logic_delay', self.total_logic_delay),
                            ('total_net_delay', self.total_net_delay)])
        return (rebuild_state, (data, ))

    def __str__(self):
        return self.thisptr.str()

    def csv_summary(self):
        return self.thisptr.csv_summary()

    property router_opts:
        def __get__(self):
            return cRouterOpts(<size_t>&self.thisptr.router_opts)

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

    property width_fac:
        def __get__(self):
            return self.thisptr.width_fac

        def __set__(self, value):
            self.thisptr.width_fac = value

    property success:
        def __get__(self):
            return self.thisptr.success

        def __set__(self, value):
            self.thisptr.success = value

    property critical_path_delay:
        def __get__(self):
            return self.thisptr.critical_path_delay

        def __set__(self, value):
            self.thisptr.critical_path_delay = value

    property tnodes_on_crit_path:
        def __get__(self):
            return self.thisptr.tnodes_on_crit_path

        def __set__(self, value):
            self.thisptr.tnodes_on_crit_path = value

    property non_global_nets_on_crit_path:
        def __get__(self):
            return self.thisptr.non_global_nets_on_crit_path

        def __set__(self, value):
            self.thisptr.non_global_nets_on_crit_path = value

    property global_nets_on_crit_path:
        def __get__(self):
            return self.thisptr.global_nets_on_crit_path

        def __set__(self, value):
            self.thisptr.global_nets_on_crit_path = value

    property total_logic_delay:
        def __get__(self):
            return self.thisptr.total_logic_delay

        def __set__(self, value):
            self.thisptr.total_logic_delay = value

    property total_net_delay:
        def __get__(self):
            return self.thisptr.total_net_delay

        def __set__(self, value):
            self.thisptr.total_net_delay = value

    def __dealloc__(self):
        del self.thisptr

    property bends:
        def __get__(self):
            if self._bends is None:
                self._bends = np.asarray(self.thisptr.bends, dtype='uint')
            return self._bends

    property wire_lengths:
        def __get__(self):
            if self._wire_lengths is None:
                self._wire_lengths = np.asarray(self.thisptr.wire_lengths,
                                                dtype='uint')
            return self._wire_lengths

    property segments:
        def __get__(self):
            if self._segments is None:
                self._segments = np.asarray(self.thisptr.segments,
                                            dtype='uint')
            return self._segments


cdef class cRouteResult(cStateBase):
    def __cinit__(self):
        self.thisptr = new RouteResult()
        self.baseptr = <StateBase *>self.thisptr

    def __reduce__(self):
        data = OrderedDict([('net_file_md5', self.net_file_md5),
                            ('arch_file_md5', self.arch_file_md5),
                            ('placed_file_md5', self.placed_file_md5),
                            ('success_channel_widths',
                             self.success_channel_widths),
                            ('failure_channel_widths',
                             self.failure_channel_widths), ])
        return (rebuild, (data, ))

    def best_channel_width(self):
        return self.thisptr.best_channel_width()

    property success_channel_widths:
        def __get__(self):
            return self.thisptr.success_channel_widths

        def __set__(self, value):
            self.thisptr.success_channel_widths = value

    property failure_channel_widths:
        def __get__(self):
            return self.thisptr.failure_channel_widths

        def __set__(self, value):
            self.thisptr.failure_channel_widths = value

    property net_file_md5:
        def __get__(self):
            cdef string s = self.thisptr.net_file_md5
            return s

        def __set__(self, value):
            self.thisptr.net_file_md5 = value

    property arch_file_md5:
        def __get__(self):
            cdef string s = self.thisptr.arch_file_md5
            return s

        def __set__(self, value):
            self.thisptr.arch_file_md5 = value

    property placed_file_md5:
        def __get__(self):
            cdef string s = self.thisptr.placed_file_md5
            return s

        def __set__(self, value):
            self.thisptr.placed_file_md5 = value

    def __dealloc__(self):
        del self.thisptr
