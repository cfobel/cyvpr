# cython: embedsignature=True
from collections import OrderedDict
import numpy as np
import os.path


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
        return self.extract_block_positions()

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

    def most_recent_route_states(self):
        states = []

        cdef int i
        cdef cRouteState state

        for i in range(g_route_states.size()):
            state = cRouteState()
            state.init(g_route_states[i])
            states.append(state)
        return states
