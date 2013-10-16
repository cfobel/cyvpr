import tables as ts
from .table_layouts import ROUTE_TABLE_LAYOUT, ROUTE_NET_DATA_TABLE_LAYOUT


class RoutingManager(object):
    '''
    Manage routing state information for placements represented in a
    `PlacementManager` instance.
    '''
    def __init__(self, placement_manager, route_database):
        self.placement_manager = placement_manager
        self.h5f = {'route_database': ts.openFile(route_database, 'a')}
        h5f = self.h5f['route_database']
        if 'routings' not in h5f.root:
            h5f.createGroup(h5f.root, 'routings')
        self.routings = h5f.root.routings

    def init_routing_group(self, vpr_net_file_namebase):
        '''
        For the specified VPR net-file namebase, create a routing group.

        __NB__ Each routing group contains:

          * A route-states table
          * A routing-per-net-data table
        '''
        h5f = self.h5f['route_database']
        if vpr_net_file_namebase in self.routings:
            raise KeyError, '"%s" table already exists.'
        net_routings = h5f.createGroup(self.routings, vpr_net_file_namebase)
        h5f.createTable(net_routings, 'route_states', ROUTE_TABLE_LAYOUT,
                        'Routing states')
        h5f.createTable(net_routings, 'route_net_data',
                        ROUTE_NET_DATA_TABLE_LAYOUT,
                        'Routing per-net data')

    def route_states_table_by_placement_md5(self, placement_md5):
        '''
        Return the route-states table corresponding to the specified placement
        file MD5 hash value.
        '''
        net_file = (self.placement_manager
                    .net_file_by_placement_md5(placement_md5))
        net_file_path = (self.placement_manager
                         .net_file_path_by_md5(net_file['md5']))
        return getattr(self.routings, net_file_path.namebase).route_states

    def route_states_by_placement_md5(self, placement_md5, width_fac=None,
                                      fast=None):
        '''
        Return the extracted row contents for any rows matching the specified:

          * Placement file MD5 hash value
          * Channel-width, _i.e., `width_fac` _(optional)_
          * VPR route `fast` setting _(optional)_

        The row contents are in the form of a tuple with named fields.

        __NB__ If a value is specified for channel-width or `fast`, only rows
        matching the respective specified value will be returned.  Otherwise,
        rows with any value for the corresponding attribute will be considered.
        '''
        placement = self.placement_manager.placement_by_md5(placement_md5)
        table = self.route_states_table_by_placement_md5(placement_md5)
        states = []
        for state in table:
            if state['placement_file_id'] != placement['id']:
                continue
            elif width_fac is not None and width_fac != state['width_fac']:
                continue
            elif fast is not None:
                # If a state was routed in `fast` mode, the following
                # attributes will be set:
                #
                # state['router_opts_']['first_iter_pres_fac'] = 10000
                # state['router_opts_']['initial_pres_fac'] = 10000
                # state['router_opts_']['bb_factor'] = 0
                # state['router_opts_']['max_router_iterations'] = 10
                #
                # For now, just check `first_iter_pres_fac`...
                if fast and state['router_options'][0] < 10000:
                    continue
                elif not fast and state['router_options'][0] == 10000:
                    continue
            states.append(state.fetch_all_fields())
        return states

    def __del__(self):
        '''
        Close any opened HDF files.
        '''
        for f in self.h5f.values():
            f.close()
