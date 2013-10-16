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
            'block_positions': ts.UInt32Col(pos=2, shape=(block_count, 3))}


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
