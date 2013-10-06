from collections import OrderedDict
from datetime import datetime

from libcpp.vector cimport vector
from libcpp.string cimport string
from libc.stdlib cimport malloc


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


def unix_time(datetime_):
    # Convert Python `datetime` instance to unix seconds-since-epoch.
    # Taken from [here] [1].
    #
    # [1]: http://stackoverflow.com/questions/6999726/python-getting-millis-since-epoch-from-datetime/11111177#11111177
    return (datetime_ - datetime.utcfromtimestamp(0)).total_seconds()


cdef datetime_from_timespec_tuple(timespec t):
    return datetime.fromtimestamp(t.tv_sec + t.tv_nsec / 1e9)


cdef class cRouteState:
    cdef RouteState this_data

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

    cdef init(self, RouteState state):
        self.this_data = state

    property start:
        def __get__(self):
            return datetime_from_timespec_tuple(self.this_data.start)

        def __set__(self, value):
            timestamp = unix_time(value)
            self.this_data.start.tv_sec = int(timestamp)
            self.this_data.start.tv_nsec = ((timestamp -
                                             self.this_data.start.tv_sec) *
                                            1e9)

    property end:
        def __get__(self):
            return datetime_from_timespec_tuple(self.this_data.end)

        def __set__(self, value):
            timestamp = unix_time(value)
            self.this_data.end.tv_sec = int(timestamp)
            self.this_data.end.tv_nsec = ((timestamp -
                                           self.this_data.end.tv_sec) * 1e9)

    property width_fac:
        def __get__(self):
            return self.this_data.width_fac

        def __set__(self, value):
            self.this_data.width_fac = value

    property success:
        def __get__(self):
            return self.this_data.success

        def __set__(self, value):
            self.this_data.success = value

    property critical_path_delay:
        def __get__(self):
            return self.this_data.critical_path_delay

        def __set__(self, value):
            self.this_data.critical_path_delay = value

    property tnodes_on_crit_path:
        def __get__(self):
            return self.this_data.tnodes_on_crit_path

        def __set__(self, value):
            self.this_data.tnodes_on_crit_path = value

    property non_global_nets_on_crit_path:
        def __get__(self):
            return self.this_data.non_global_nets_on_crit_path

        def __set__(self, value):
            self.this_data.non_global_nets_on_crit_path = value

    property global_nets_on_crit_path:
        def __get__(self):
            return self.this_data.global_nets_on_crit_path

        def __set__(self, value):
            self.this_data.global_nets_on_crit_path = value

    property total_logic_delay:
        def __get__(self):
            return self.this_data.total_logic_delay

        def __set__(self, value):
            self.this_data.total_logic_delay = value

    property total_net_delay:
        def __get__(self):
            return self.this_data.total_net_delay

        def __set__(self, value):
            self.this_data.total_net_delay = value


cdef class cRouteResult:
    cdef RouteResult *thisptr

    def __cinit__(self):
        self.thisptr = new RouteResult()

    def __reduce__(self):
        data = OrderedDict([('success_channel_widths',
                              self.success_channel_widths),
                            ('failure_channel_widths',
                             self.failure_channel_widths),
                            ('critical_path_delay', self.critical_path_delay),
                            ('tnodes_on_crit_path', self.tnodes_on_crit_path),
                            ('non_global_nets_on_crit_path',
                             self.non_global_nets_on_crit_path),
                            ('global_nets_on_crit_path',
                             self.global_nets_on_crit_path),
                            ('total_logic_delay', self.total_logic_delay),
                            ('total_net_delay', self.total_net_delay),
                            ('net_file_md5', self.net_file_md5),
                            ('arch_file_md5', self.arch_file_md5),
                            ('placed_file_md5', self.placed_file_md5), ])
        return (rebuild, (data, ))

    cdef set(self, RouteResult result):
        self.thisptr.set(result)

    def __str__(self):
        return self.thisptr.str()

    def csv(self):
        return self.thisptr.csv()

    property csv_header:
        def __get__(self):
            return self.thisptr.csv_header()

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

    def get_net_file_md5(self):
        print self.thisptr.net_file_md5.c_str()

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


def vpr(args):
    cdef int argc = len(args) + 1
    cdef char **argv = <char **> malloc(argc * sizeof(char *))
    cdef vector[string] args_

    args_.push_back("./vpr")
    for a in args:
        args_.push_back(str(a))

    cdef int i
    for i in xrange(args_.size()):
        argv[i] = <char *>args_[i].c_str()
    print __main__(args_.size(), argv)


def vpr_place(net_path, output_path, fast=True, seed=0):
    args = [net_path, '/var/benchmarks/4lut_sanitized.arch', output_path,
            'routed.out', '-place_only', '-fast', '-place_algorithm',
            'bounding_box', '-nodisp', '-seed', str(seed)]
    vpr(args)


def vpr_route(net_path, placed_path, output_path, fast=True):
    args = [net_path, '/var/benchmarks/4lut_sanitized.arch', placed_path,
            output_path, '-route_only', '-fast', '-nodisp']
    print '[vpr_route] args:', args
    vpr(args)
    # Tnodes on critical path.
    print 'tnodes_on_crit_path:', g_route_result.tnodes_on_crit_path
    # Non-global nets on critical path.
    print 'non_global_nets_on_crit_path:', g_route_result.non_global_nets_on_crit_path
    # Global nets on critical path.
    print 'global_nets_on_crit_path:', g_route_result.global_nets_on_crit_path
    # Total logic delay
    print 'total_logic_delay:', g_route_result.total_logic_delay
    # Total net delay.
    print 'total_net_delay:', g_route_result.total_net_delay
    print 'critical path delay:', g_route_result.critical_path_delay
    print 'routed successfully with the following channel widths:', g_route_result.success_channel_widths
    print 'failed to route with the following channel widths:', g_route_result.failure_channel_widths

    cy_result = cRouteResult()
    cy_result.set(g_route_result)

    states = []
    cdef int i
    cdef cRouteState state
    for i in range(g_route_states.size()):
        state = cRouteState()
        state.init(g_route_states[i])
        states.append(state)
    return g_args, cy_result, states


def test():
    result = cRouteResult()
    result.set(g_route_result)
    return result
