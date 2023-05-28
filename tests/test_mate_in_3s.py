import os
import sys

from tqdm import tqdm

thisdir = os.path.dirname(os.path.abspath(__file__))
p_to_src = os.path.abspath(os.path.dirname(thisdir))
sys.path.append(p_to_src)
import cProfile
import pstats
from pathlib import Path

from src.board import Board, Move
from src.searcher_ab_ids_hsh_q import Searcher as ABTTQSearcher
from src.searcher_alphabeta import Searcher as ABSearcher
from src.searcher_pvs import Searcher as PVSearcher

profiler = cProfile.Profile()


def test_mate_in_threes(fen_filter):
    fname = './data/mate_in_3.txt'

    data = open(fname).read().splitlines()
    data = [d for d in data if d != '']
    # s = ABSearcher
    valid_fens = []
    for datum in data:
        try:
            Board(datum)
            valid_fens.append(datum)
        except:
            continue

    valid_fens.sort()

    invalid_fens = []
    for fen in tqdm(valid_fens):
        if fen_filter != None and fen != fen_filter:
            continue
        board = Board(fen)
        # print(board)
        s = ABTTQSearcher()
        # s = ABSearcher()
        s = PVSearcher()
        print(fen)
        # score, moves = s._search_at_depth(board,depth=5, can_null = True)
        profiler.enable()
        score, moves = s.find_move(board, depth=5)
        profiler.disable()
        for m in moves:
            board.push(Move.from_uci(m))
        try:
            assert board.is_checkmate(), board
        except:
            print(f'Didn\'t find mate in 3 for fen {fen}')
            invalid_fens.append(fen)
            # import pdb; pdb.set_trace()

    print(f'Found {len(valid_fens) - len(invalid_fens)}/{len(valid_fens)} valid, {len(invalid_fens)} invalid')
    import pdb

    pdb.set_trace()


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('--fen')
    p.add_argument('-o', type=str, default='')
    args = p.parse_args()
    fen = args.fen
    try:
        test_mate_in_threes(fen)
    except KeyboardInterrupt:
        pass

    # still dump stats
    out_f = args.o

    # dump stats
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    import datetime

    dt = datetime.datetime.now()
    out_p = Path('./stats_m3')

    if not out_p.exists():
        out_p.mkdir(exist_ok=True, parents=True)

    if out_f != '':
        out_p = out_p / out_f
    else:
        out_p = out_p / f"run_{dt.strftime('%Y_%m_%d')}.prof"

    stats.dump_stats(str(out_p))
    print(f'Stats dumped to {out_f}')
