# cython: embedsignature=True
from libc.stdint cimport uint32_t

from collections import OrderedDict
import sys
import os.path

import numpy as np


cpdef bounding_box_cross_count(int net_block_count):
    cdef float crossing

    if net_block_count > 50:
        crossing = 2.7933 + 0.02616 * (net_block_count - 50)
    else:
        crossing = cross_count[net_block_count - 1];

    return crossing


cdef uint32_t INFINITY = sys.maxint


cdef class cStarPlusData:
    cdef public float x_sum
    cdef public float x_squared_sum
    cdef public float y_sum
    cdef public float y_squared_sum
    cdef float alpha
    cdef float beta

    def __cinit__(self, float alpha=1.59, float beta=1.):
        self.alpha = alpha
        self.beta = beta
        self.reset()

    def update(self, x, y):
        self.x_sum += x
        self.x_squared_sum += x * x
        self.y_sum += y
        self.y_squared_sum += y * y

    def reset(self):
        self.x_sum = 0
        self.x_squared_sum = 0
        self.y_sum = 0
        self.y_squared_sum = 0

    def cost(self, uint32_t net_block_count):
        return self.alpha * (np.sqrt(self.x_squared_sum - (self.x_sum *
                                                           self.x_sum) /
                                     net_block_count + self.beta) +
                             np.sqrt(self.y_squared_sum - (self.y_sum *
                                                           self.y_sum) /
                                     net_block_count + self.beta))


cdef class cBoundingBoxData:
    cdef public uint32_t min_x
    cdef public uint32_t max_x
    cdef public uint32_t min_y
    cdef public uint32_t max_y

    def __cinit__(self):
        self.reset()

    def update(self, x, y):
        self.min_x = min(x, self.min_x)
        self.max_x = max(x, self.max_x)
        self.min_y = min(y, self.min_y)
        self.max_y = max(y, self.max_y)

    def reset(self):
        self.min_x = INFINITY
        self.max_x = 0
        self.min_y = INFINITY
        self.min_y = 0

    def cost(self, uint32_t net_block_count):
        cdef float cross_count = bounding_box_cross_count(net_block_count)
        return cross_count * (self.max_x - self.min_x + self.max_y - self.min_y)


cpdef compute_bounding_box_cost(uint32_t [:] net_keys, uint32_t [:] block_keys,
                                uint32_t [:] net_connection_counts,
                                uint32_t [:, :] block_positions):
    cdef double total_net_cost = 0.
    cdef object bbox = cBoundingBoxData()

    cdef int i
    cdef int net_key
    cdef int block_key

    cdef int prev_net_key = -1

    for i in xrange(len(net_keys)):
        net_key = net_keys[i]
        block_key = block_keys[i]

        if net_key != prev_net_key:
            if prev_net_key > 0:
                # Compute bounding-box for `prev_net_key`.
                net_block_count = net_connection_counts[prev_net_key]
                total_net_cost += bbox.cost(net_block_count)
            bbox.reset()
            prev_net_key = net_key
        x = block_positions[block_key][0]
        y = block_positions[block_key][1]
        bbox.update(x, y)
    # Compute bounding-box for last net.
    total_net_cost += bbox.cost(net_connection_counts[net_key])
    return total_net_cost


cpdef compute_star_plus_cost(uint32_t [:] net_keys, uint32_t [:] block_keys,
                             uint32_t [:] net_connection_counts,
                             uint32_t [:, :] block_positions):
    cdef double total_net_cost = 0.
    cdef object star_plus = cStarPlusData()

    cdef int i
    cdef int net_key
    cdef int block_key

    cdef int prev_net_key = -1

    for i in xrange(len(net_keys)):
        net_key = net_keys[i]
        block_key = block_keys[i]

        if net_key != prev_net_key:
            if prev_net_key > 0:
                # Compute bounding-box for `prev_net_key`.
                net_block_count = net_connection_counts[prev_net_key]
                total_net_cost += star_plus.cost(net_block_count)
            star_plus.reset()
            prev_net_key = net_key
        x = block_positions[block_key][0]
        y = block_positions[block_key][1]
        star_plus.update(x, y)
    # Compute bounding-box for last net.
    total_net_cost += star_plus.cost(net_connection_counts[net_key])
    return total_net_cost


def bounding_box(block_positions):
    '''
    Return the bounding-box cost for the specified block-positions.

    Notes
    =====

    `block_positions` must be a two-dimensional numpy array _(or provide the
    same interface)_, where the dimensions of `block_positions` are indexed as
    follows:

        block-index, x=0/y=1/...

    For example, consider two blocks, with the following positions:

        - `(x=3, y=7)`
        - `(x=5, y=2)`

    The corresponding `block_positions` array would be:

        np.array([[3, 7], [5, 2]])
    '''
    return (bounding_box_cross_count(len(block_positions)) *
            ((block_positions[:, :2].max(axis=0) -
              block_positions[:, :2].min(axis=0))).sum())


cdef class cMain:
    cdef Main *thisptr
    cdef bint _initialized

    def __cinit__(self):
        self.thisptr = new Main()
        self._initialized = False

    def read_placement(self, net_file, arch_file, place_file):
        args = [net_file, arch_file, place_file, 'routed.out',
                '-place_only']

        self.init(args)
        self.do_read_place()
        return self.extract_block_positions()

    def do_read_place(self):
        if 'placed' not in self.file_paths:
            raise RuntimeError, 'No placement file has been specified.'
        if not os.path.isfile(self.file_paths['placed']):
            raise IOError, ('Could not access placement file: %s' %
                            self.file_paths['placed'])
        self.thisptr.do_read_place()

    def extract_block_positions(self):
        '''
        Extract block-positions from VPR data structures and convert the
        positions to a Numpy array, with dimensions indexed as follows:

            block-index, x=0/y=1/slot-index=2
        '''
        block_positions = np.empty((self.block_count, 3), dtype='uint')
        cdef int i
        cdef int j
        block_position_vectors = extract_block_positions()
        for i in xrange(self.block_count):
            for j in xrange(3):
                block_positions[i, j] = block_position_vectors[i][j]
        return block_positions

    def init(self, args):
        cdef int argc = len(args) + 1
        cdef char **argv = <char **> malloc(argc * sizeof(char *))
        cdef vector[string] args_

        args_.push_back("./vpr")
        for a in args:
            args_.push_back(str(a))

        cdef int i
        for i in xrange(args_.size()):
            argv[i] = <char *>args_[i].c_str()
        self.thisptr.init(argc, argv)
        self._initialized = True

    def place(self, net_path, arch_file, output_path,
              place_algorithm='bounding_box', fast=True, seed=0):
        args = [net_path, arch_file, output_path, 'routed.out', '-place_only',
                '-place_algorithm', place_algorithm, '-nodisp', '-seed',
                str(seed)]

        if fast:
            args += ['-fast']

        self.init(args)
        self.thisptr.do_place_and_route()
        return self.most_recent_place_state(), self.extract_block_positions()

    property router_opts:
        def __get__(self):
            return cRouterOpts(<size_t>&self.thisptr.router_opts_)

    def set_router_opts(self, fast):
        if fast:
            self.thisptr.router_opts_.first_iter_pres_fac = 10000
            self.thisptr.router_opts_.initial_pres_fac = 10000
            self.thisptr.router_opts_.bb_factor = 0
            self.thisptr.router_opts_.max_router_iterations = 10
        else:
            self.thisptr.router_opts_.first_iter_pres_fac = 0.5
            self.thisptr.router_opts_.initial_pres_fac = 0.5
            self.thisptr.router_opts_.bb_factor = 3
            self.thisptr.router_opts_.max_router_iterations = 30

    def route_again(self, int route_chan_width, fast=False):
        if not self._initialized:
            raise RuntimeError, '`init` method must be run first.'
        self.set_router_opts(fast)
        return self.thisptr.route(route_chan_width)

    def route(self, net_path, arch_file, placed_path, output_path,
              timing_driven=True, fast=False, route_chan_width=None,
              max_router_iterations=None):
        '''
        Router Options:
            [-max_router_iterations <int>] [-bb_factor <int>]
            [-initial_pres_fac <float>] [-pres_fac_mult <float>]
            [-acc_fac <float>] [-first_iter_pres_fac <float>]
            [-bend_cost <float>] [-route_type global | detailed]
            [-verify_binary_search] [-route_chan_width <int>]
            [-router_algorithm breadth_first | timing_driven]
            [-base_cost_type intrinsic_delay | delay_normalized | demand_only]

        Routing options valid only for timing-driven routing:
            [-astar_fac <float>] [-max_criticality <float>]
            [-criticality_exp <float>]
        '''
        args = [net_path, arch_file, placed_path,
                output_path, '-route_only', '-nodisp', '-router_algorithm']
        if timing_driven:
            args += ['timing_driven']
        else:
            args += ['breadth_first']

        if route_chan_width is not None:
            args += ['-route_chan_width', route_chan_width]

        if max_router_iterations is not None:
            args += ['-max_router_iterations', max_router_iterations]

        if fast:
            args += ['-fast']

        self.init(args)
        self.thisptr.do_place_and_route()
        return OrderedDict([
            ('result', self.most_recent_route_result()),
            ('states', self.most_recent_route_states()),
        ])

    property net_count:
        def __get__(self):
            return self.thisptr.net_count()

    property block_count:
        def __get__(self):
            return self.thisptr.block_count()

    property file_paths:
        def __get__(self):
            return self.thisptr.filepath_

    property file_md5s:
        def __get__(self):
            return self.thisptr.file_md5_

    property pins_per_clb:
        def __get__(self):
            return pins_per_clb

    def most_recent_args(self):
        return g_args

    def most_recent_route_result(self):
        cy_result = cRouteResult()
        cy_result.set(g_route_result)
        return cy_result

    def most_recent_place_state(self):
        cdef cPlaceState state

        state = cPlaceState()
        state.init(g_place_state)
        return state

    def most_recent_route_states(self):
        states = []

        cdef int i
        cdef cRouteState state

        for i in range(g_route_states.size()):
            state = cRouteState()
            state.init(g_route_states[i])
            states.append(state)
        return states
