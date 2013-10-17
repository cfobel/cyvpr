import tables as ts


NET_FILES_TABLE_LAYOUT = {'md5': ts.StringCol(32, pos=1),
                          'block_count': ts.UInt32Col(pos=2),
                          'net_count': ts.UInt32Col(pos=3)}
ROUTE_TABLE_LAYOUT = {'id': ts.UInt64Col(pos=0),
                      'net_file_id': ts.UInt64Col(pos=1),
                      'placement_file_id': ts.UInt64Col(pos=2),
                      'success': ts.BoolCol(pos=3),
                      'width_fac': ts.UInt32Col(pos=4),
                      'start': ts.Float64Col(pos=5),
                      'end': ts.Float64Col(pos=6),
                      'router_options': {'first_iter_pres_fac':
                                         ts.Float32Col(pos=0),
                                         'initial_pres_fac':
                                         ts.Float32Col(pos=1),
                                         'pres_fac_mult': ts.Float32Col(pos=2),
                                         'acc_fac': ts.Float32Col(pos=3),
                                         'bend_cost': ts.Float32Col(pos=4),
                                         'bb_factor': ts.Int32Col(pos=5),
                                         'astar_fac': ts.Float32Col(pos=6),
                                         'max_criticality':
                                         ts.Float32Col(pos=7),
                                         'criticality_exp':
                                         ts.Float32Col(pos=8), },
                      'net_data_offset': ts.UInt64Col(pos=8),
                      'net_count': ts.UInt32Col(pos=9)}
ROUTE_NET_DATA_TABLE_LAYOUT = {'id': ts.UInt64Col(pos=0),
                               'route_id': ts.UInt64Col(pos=1),
                               'net_data': {'bends': ts.UInt32Col(pos=0),
                                            'wire_length': ts.UInt32Col(pos=1),
                                            'segments': ts.UInt32Col(pos=2)}}


def get_PLACEMENT_TABLE_LAYOUT(block_count):
    return {'net_file_md5': ts.StringCol(32, pos=0),
            'seed': ts.UInt32Col(pos=1),
            'block_positions_sha1': ts.StringCol(40, pos=2),
            'block_positions': ts.UInt32Col(pos=2, shape=(block_count, 3)),
            'start': ts.Float64Col(pos=4),
            'end': ts.Float64Col(pos=5),
            'placer_options': {'timing_tradeoff': ts.Float32Col(pos=0),
                               'block_dist': ts.UInt32Col(pos=1),
                               'place_cost_exp': ts.Float32Col(pos=2),
                               'place_chan_width': ts.UInt32Col(pos=3),
                               'num_regions': ts.UInt32Col(pos=4),
                               'recompute_crit_iter': ts.UInt32Col(pos=5),
                               'enable_timing_computations': ts.BoolCol(pos=6),
                               'inner_loop_recompute_divider':
                               ts.UInt32Col(pos=7),
                               'td_place_exp_first': ts.Float32Col(pos=8),
                               'td_place_exp_last': ts.Float32Col(pos=9),
                               'place_cost_type': ts.UInt8Col(pos=10),
                               'place_algorithm': ts.UInt8Col(pos=11),}}


def get_VPR_PLACEMENT_STATS_TABLE_LAYOUT():
    '''
    This table layout contains all fields printed in the summary table during a
    VPR _place_ operation.  It also includes two unix-timestamps, `start` and
    `end`, which mark the start-time and end-time of the corresponding
    outer-loop iteration, respectively.
    '''
    return {'start': ts.Float64Col(pos=1),
            'end': ts.Float64Col(pos=2),
            'temperature': ts.Float32Col(pos=3),
            'mean_cost': ts.Float64Col(pos=4),
            'mean_bounding_box_cost': ts.Float64Col(pos=5),
            'mean_timing_cost': ts.Float64Col(pos=6),
            'mean_delay_cost': ts.Float64Col(pos=7),
            'place_delay_value': ts.Float32Col(pos=8),
            'success_ratio': ts.Float32Col(pos=9),
            'std_dev': ts.Float64Col(pos=10),
            'radius_limit': ts.Float32Col(pos=11),
            'criticality_exponent': ts.Float32Col(pos=12),
            'total_iteration_count': ts.UInt32Col(pos=13),}


def get_ROUTE_TABLE_LAYOUT(net_count):
    return {'id': ts.UInt32Col(pos=0),
            'net_file_id': ts.UInt32Col(pos=1),
            'placement_file_id': ts.UInt32Col(pos=2),
            'success': ts.BoolCol(pos=3),
            'width_fac': ts.UInt32Col(pos=4),
            'start': ts.Float64Col(pos=5),
            'end': ts.Float64Col(pos=6),
            'router_options': {'first_iter_pres_fac':
                                ts.Float32Col(pos=0),
                                'initial_pres_fac':
                                ts.Float32Col(pos=1),
                                'pres_fac_mult': ts.Float32Col(pos=2),
                                'acc_fac': ts.Float32Col(pos=3),
                                'bend_cost': ts.Float32Col(pos=4),
                                'bb_factor': ts.Int32Col(pos=5),
                                'astar_fac': ts.Float32Col(pos=6),
                                'max_criticality':
                                ts.Float32Col(pos=7),
                                'criticality_exp':
                                ts.Float32Col(pos=8), },
            'net_data': {'bends': ts.UInt32Col(pos=0, shape=(net_count, )),
                        'wire_length': ts.UInt32Col(pos=1, shape=(net_count, )),
                        'segments': ts.UInt32Col(pos=2, shape=(net_count, ))}}
