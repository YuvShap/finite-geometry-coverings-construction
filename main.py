import argparse
from multiprocessing.connection import Client

from coverings_constructor import CoveringConstructor

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--q', type=int, default=None, help='geometry parameter')
    parser.add_argument('--m', type=int, default=None, help='geometry parameter')
    parser.add_argument('--t', type=int, default=None, help='geometry parameter')
    parser.add_argument('--num_of_parts', type=int, default=1, help='the number of disjoint parts of the covering')
    parser.add_argument('--part_index', type=int, default=0, help='the index of the part to construct')
    parser.add_argument('--chosen_points_indices_str', type=str, default=None, help='a string representing the indices of the points of the geometry in which to induce the construction. If None, induce on all points')
    parser.add_argument('--port', type=int, default=None, help='the port on localhost to send the blocks to. If None, output the blocks to stdout')

    args = parser.parse_args()
    assert args.q is not None
    assert args.m is not None
    assert args.t is not None

    total_number_of_points = int((args.q ** (args.m + 1) - 1) / (args.q - 1))
    chosen_points_indices = [int(item) for item in args.chosen_points_indices_str.split(',')] if args.chosen_points_indices_str is not None else list(range(total_number_of_points))
    coverings_constructor = CoveringConstructor(q=args.q, m=args.m, t=args.t, chosen_points_indices=chosen_points_indices)

    if args.port is None:
        coverings_constructor.stream_induced_covering(part_index=args.part_index,
                                                      num_of_parts=args.num_of_parts, conn=None)
    else:
        address = ('localhost', args.port)
        with Client(address) as conn:
            coverings_constructor.stream_induced_covering(part_index=args.part_index,
                                                          num_of_parts=args.num_of_parts, conn=conn)

            message = conn.recv()
            assert message == 'done'
            conn.send('done')

