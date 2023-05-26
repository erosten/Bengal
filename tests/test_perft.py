import sys, os

p_to_src = os.path.abspath(os.path.dirname(os.path.abspath('')))
sys.path.append(p_to_src)

from src.chess import Board

def perft_test(depth: int, board: Board) -> int:
    if depth >= 1:
        count = 0

        for move in board.generate_sorted_moves():
            board.push(move)
            count += perft_test(depth - 1, board)
            board.pop()

        return count
    else:
      return 1
    
def perft(depth: int, board: Board) -> int:
    if depth >= 1:
        count = 0

        for move in board.generate_legal_moves():
            board.push(move)
            count += perft(depth - 1, board)
            board.pop()

        return count
    else:
      return 1

import time
import json
from tqdm import tqdm

def test(fens):
    n1 = []
    n2 = []
    for fen in fens:
        b = Board(fen)
        d = 3
        pnodes = perft(d, b)
        pnodes2 = perft_test(d, b)

        n1.append(pnodes)
        n2.append(pnodes2)
    
    print('Reg ', n1)
    print('Test ', n2)



from typing import Tuple, List
def gen(additional_tests: List[Tuple[str, int]] = []):
    json_out = []
    n1 = []
    n2 = []
    from data.original_search_test_data import DATA
    d = sorted(DATA, key = lambda x: x['depth'])
    for test in tqdm(d):
        # if test['depth'] >= 4:
        #     continue
        print(test)
        out = {}
        n = test['nodes']
        d = test['depth']
        n1.append(n)

        fen = test['fen']
        out['nodes'] = n
        out['depth'] = d
        out['fen'] = fen
        b = Board(fen)
        t1 = time.time()
        n = perft_test(d, b)
        t = time.time()-t1
        out['perft_time'] = t
        out['perft_nodes'] = n
        n2.append(n)
        json_out.append(out)
    

    
    # assumed no GT
    for (fen, d) in additional_tests:
        out = {}
        print(fen)
        b=Board(fen)
        t1 = time.time()
        n = perft(d,b)
        t = time.time()-t1
        out['nodes'] = n
        n1.append(n)
        out['depth'] = d
        out['fen'] = fen
        t1 = time.time()
        n = perft_test(d,b)
        t = time.time()-t1
        out['perft_time'] = t
        out['perft_nodes'] = n
        n2.append(n)
        json_out.append(out)
        

    json_formatted_str = json.dumps(json_out, indent=2)

    print(json_formatted_str)
    equal = [x == y for x,y in zip(n1, n2)]

    print(f'Perft passing: {sum(equal)}/{len(n1)}')
    import pdb; pdb.set_trace()


ADDITIONAL_DATA = [
    ('r2Q1k1r/ppp1bppp/4b3/1B6/5q2/2P5/PPP2PPP/R3R1K1 w - - 0 2', 3),
    ('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 4)
]

if __name__ == '__main__':
    gen(additional_tests=ADDITIONAL_DATA)
    # test(fens = [])
    # test(fens = ['r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10'])