from path_helpers import path
from cyvpr.Main import cMain
import cyvpr


def test_route():
    data_root = path(cyvpr.get_data_root()[0])
    arch = data_root.joinpath('4lut_sanitized.arch')
    net = data_root.joinpath('e64-4lut.net')
    m = cMain()
    block_positions = m.place(net, arch, 'placed.out')
    assert(len(block_positions) == m.block_count)
    routed_data = m.route(net, arch, 'placed.out', 'routed.out')
    state = [s for s in routed_data['states'] if s.success][-1]
    assert(len(state.wire_lengths) == m.net_count)
    assert(len(state.bends) == m.net_count)
    assert(len(state.segments) == m.net_count)
    return routed_data


if __name__ == '__main__':
    routed_data = test_route()
    state = [s for s in routed_data['states'] if s.success][-1]
    print state.wire_lengths
    print state.bends
    print state.segments
