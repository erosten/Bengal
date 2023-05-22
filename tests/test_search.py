import sys, os
import json
from pathlib import Path

thisdir= os.path.dirname(os.path.abspath(__file__))
p_to_src = os.path.abspath(os.path.dirname(thisdir))
sys.path.append(p_to_src)
from src.searcher_negamax import Searcher
from src.searcher_alphabeta import Searcher as ABSearcher
from src.searcher_ab_ids_hsh import Searcher as ABTTSearcher
# from src.pv_searcher import PrincipalVariationSearcher as PVSearcher
from src.chess import Board
from src.utils import display
from src.searcher_ab_ids_hsh_q import Searcher as ABTTQSearcher
import time
import cProfile, pstats
from tqdm import tqdm
import tabulate

def load_data():
   with open(os.path.join(thisdir, 'search_test_data.json'), 'r') as f:
      return json.load(f)


profiler = cProfile.Profile()



def test(filter=None):
   d = load_data()
   results = []

   for test in tqdm(d):
      n = test['nodes']
      d = test['depth']
      fen = test['fen']
      if filter and fen != filter:
         continue

      b = Board(fen)
      s = Searcher()
      # s = PVSearcher()
      s = ABSearcher()
      s = ABTTQSearcher()
      t1 = time.time()
      profiler.enable()
      # score,m = s._search_at_depth(b,depth=d)
      score,m = s._search_at_depth(b,depth=d)
      profiler.disable()

      t = time.time() - t1
      results.append((test, (t,m, s.nodes, score)))
   return results


if __name__ == '__main__':
   import argparse
   parser = argparse.ArgumentParser()
   parser.add_argument('-o', type=str, default='')
   parser.add_argument('--filter', default=None)
   args = parser.parse_args()
   out_f = args.o
   filter = args.filter
   res = test(filter)

   # dump stats
   stats = pstats.Stats(profiler).sort_stats('cumtime')
   import datetime
   dt = datetime.datetime.now()
   out_p = Path('./search_test_stats')

   if not out_p.exists():
      out_p.mkdir(exist_ok=True, parents=True)

   if out_f != '':
      out_p = out_p / out_f
   else:
      out_p = out_p / f"run_{dt.strftime('%Y_%m_%d')}.prof"
   
   stats.dump_stats(str(out_p))
   print(f'Stats dumped to {out_f}')

   data = [(
         t['depth'], t['nodes'], ts_n, # Nodes
         t['perft_time'], t['mini_time'], ts_t, # Time
         t['mini_move'], ts_m, t['best_move'], # Moves
         t['mini_score'], ts_s, # Scores
         t['comments'] # Comments
      )
      for t, (ts_t, ts_m, ts_n, ts_s) in res
   ]
   data.sort(key = lambda x: x[1], reverse=True) # sort by nodes, most at top
   headers = [
         'Depth',
         'Nodes',
         'TS Nodes*',
         'perft (s)',
         'mini (s)',
         'TS (s)*',
         'mini (mv)',
         'TS* (mv)',
         'best',
         'mini',
         'TS*',
         ''
      ]
   
   table = tabulate.tabulate(
      data,
      headers = headers,
      tablefmt = 'grid'
   )

   print(table)
      
   
