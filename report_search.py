import cProfile
import pstats
import time
from pathlib import Path

from src.board import Board, Move
from src.searcher_pvs import Searcher as PVSearcher
from src.utils import display

profiler = cProfile.Profile()


def test(fen=None):

    # b = Board(fen="r1bq1b1r/ppp3pp/2n1k3/3np3/2B5/5Q2/PPPP1PPP/RNB1K2R w KQha - 0 1")
    b = Board(fen)
    s = PVSearcher()
    b.push(Move.from_uci('e3f3'))
    s.pos_hist.add(b._board_pieces_state())
    b.push(Move.from_uci('f5e4'))
    s.pos_hist.add(b._board_pieces_state())
    b.push(Move.from_uci('f3e3'))
    s.pos_hist.add(b._board_pieces_state())
    b.push(Move.from_uci('e4f5'))
    s.pos_hist.add(b._board_pieces_state())
    b.push(Move.from_uci('e3f3'))
    s.pos_hist.add(b._board_pieces_state())
    b.push(Move.from_uci('f5e4'))
    # s.pos_hist.add(b.copy())
    import pdb

    pdb.set_trace()
    display(b)
    t1 = time.time()
    profiler.enable()
    # score,m = s._search_at_depth(b,depth=d)
    score, m = s.find_move(b, depth=7)
    profiler.disable()

    t = time.time() - t1
    return (test, (t, m, s.nodes, score))


# https://www.stmintz.com/ccc/index.php?id=143331
# rnbqkbnr/ppp2ppp/8/3pp3/3PP3/8/PPP2PPP/RNBQKBNR w - - 0 1
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', type=str, default='')
    parser.add_argument('--fen', default=None)
    args = parser.parse_args()
    out_f = args.o
    fen = args.fen

    res = test(fen)
    print(res)

    # dump stats
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    import datetime

    dt = datetime.datetime.now()
    out_p = Path('./report_search_profiling')

    if not out_p.exists():
        out_p.mkdir(exist_ok=True, parents=True)

    if out_f != '':
        out_p = out_p / out_f
    else:
        out_p = out_p / f"run_{dt.strftime('%Y_%m_%d')}.prof"

    stats.dump_stats(str(out_p))
    print(f'Stats dumped to {out_f}')
