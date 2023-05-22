import sys, os

p_to_src = os.path.abspath(os.path.dirname(os.path.abspath('')))
sys.path.append(p_to_src)

# from src.search import Searcher
from src.searcher_negamax import Searcher
from src.searcher_alphabeta import Searcher as ABSearcher
from src.board_state import BoardState
from src.utils import display
from tqdm import tqdm


import chess
def perft(depth: int, board: chess.Board) -> int:
    if depth >= 1:
        count = 0

        for move in board.legal_moves:
            board.push(move)
            count += perft(depth - 1, board)
            board.pop()

        return count
    else:
      return 1

import time
import json
def gen():
   json_out = []
   from data.original_search_test_data import DATA
   d = sorted(DATA, key = lambda x: x['depth'])
   for test in tqdm(d):
      print(test)
      out = {}
      n = test['nodes']
      d = test['depth']
      fen = test['fen']
      out['nodes'] = n
      out['depth'] = d
      out['fen'] = fen
      out['comments'] = test['comments']
      out['best_move'] = test['best_move']
      b1 = BoardState(fen)
      b2 = chess.Board(fen)
      s = Searcher()
      display(b1)
      t1 = time.time()
      score, m = s._search_at_depth(b1,depth=d)
      t=time.time()-t1
      out['mini_move'] = m.uci()
      out['mini_time'] = t
      out['mini_nodes'] = s.nodes
      out['mini_score'] = score
      t1 = time.time()
      perft(d, b2)
      t = time.time()-t1
      out['perft_time'] = t
      json_out.append(out)
    
   with open('search_test_data.json', 'w') as o:
      json.dump(json_out, o, indent=4)




if __name__ == '__main__':
    gen()
