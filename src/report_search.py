import sys, os
import json
from pathlib import Path

thisdir= os.path.dirname(os.path.abspath(__file__))
p_to_src = os.path.abspath(os.path.dirname(thisdir))
sys.path.append(p_to_src)

from src.chess import Board
from src.utils import display
from src.searcher_ab_ids_hsh_q import Searcher as ABTTQSearcher
import time
import cProfile, pstats
from tqdm import tqdm
import tabulate



profiler = cProfile.Profile()



def test(fen=None):

    # b = Board(fen="r1bq1b1r/ppp3pp/2n1k3/3np3/2B5/5Q2/PPPP1PPP/RNB1K2R w KQha - 0 1")
    b = Board(fen)
    display(b)
    s = ABTTQSearcher()
    t1 = time.time()
    profiler.enable()
    # score,m = s._search_at_depth(b,depth=d)
    score,m = s._search_at_depth(b,depth=20)
    profiler.disable()

    t = time.time() - t1
    return (test, (t,m, s.nodes, score))


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
#    # dump stats
#    stats = pstats.Stats(profiler).sort_stats('cumtime')
#    import datetime
#    dt = datetime.datetime.now()
#    out_p = Path('./search_test_stats')

#    if not out_p.exists():
#       out_p.mkdir(exist_ok=True, parents=True)

#    if out_f != '':
#       out_p = out_p / out_f
#    else:
#       out_p = out_p / f"run_{dt.strftime('%Y_%m_%d')}.prof"
   
#    stats.dump_stats(str(out_p))
#    print(f'Stats dumped to {out_f}')

#    data = [(
#          t['depth'], t['nodes'], ts_n, # Nodes
#          t['perft_time'], t['mini_time'], ts_t, # Time
#          t['mini_move'], ts_m, t['best_move'], # Moves
#          t['mini_score'], ts_s, # Scores
#          t['comments'] # Comments
#       )
#       for t, (ts_t, ts_m, ts_n, ts_s) in res
#    ]
#    data.sort(key = lambda x: x[1], reverse=True) # sort by nodes, most at top
#    headers = [
#          'Depth',
#          'Nodes',
#          'TS Nodes*',
#          'perft (s)',
#          'mini (s)',
#          'TS (s)*',
#          'mini (mv)',
#          'TS* (mv)',
#          'best',
#          'mini',
#          'TS*',
#          ''
#       ]
   
#    table = tabulate.tabulate(
#       data,
#       headers = headers,
#       tablefmt = 'grid'
#    )

#    print(table)
      
   
