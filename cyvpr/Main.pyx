from collections import OrderedDict
import numpy as np
import os.path


cdef class cMain:
    cdef Main *thisptr

    def __cinit__(self):
        self.thisptr = new Main()

    def read_placement(self, arch_file, net_file, place_file):
        cdef vector[string] args_

        args_.push_back("./vpr")
        args_.push_back(net_file)
        args_.push_back(arch_file)
        args_.push_back(place_file)
        args_.push_back('routed.out')
        args_.push_back('-place_only')

        cdef int argc = args_.size()
        cdef char **argv = <char **> malloc(argc * sizeof(char *))
        cdef int i
        for i in xrange(argc):
            argv[i] = <char *>args_[i].c_str()
        self.thisptr.init(argc, argv)
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

    def route(self, net_path, arch_file, placed_path, output_path,
              timing_driven=True, fast=False):
        args = [net_path, '/var/benchmarks/4lut_sanitized.arch', placed_path,
                output_path, '-route_only', '-nodisp', '-router_algorithm']
        if timing_driven:
            args += ['timing_driven']
        else:
            args += ['breadth_first']

        if fast:
            args += ['-fast']

        self.init(args)
        try:
            self.thisptr.do_place_and_route()
            signal_caught = None
        except RuntimeError, e:
            warnings.warn('Stopped by signal - ' + str(e))
            signal_caught = str(e)

        cy_result = cRouteResult()
        cy_result.set(g_route_result)

        states = []

        cdef int i
        cdef cRouteState state

        for i in range(g_route_states.size()):
            state = cRouteState()
            state.init(g_route_states[i])
            states.append(state)
        return OrderedDict([
            ('args', g_args),
            ('signal_caught', signal_caught),
            ('result', cy_result),
            ('states', states),
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
