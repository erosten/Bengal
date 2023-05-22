#!/bin/sh
import chess
import chess.pgn
import chess.engine
import os, sys
thisdir= os.path.dirname(os.path.abspath(__file__))
p_to_src = os.path.abspath(os.path.dirname(thisdir))
sys.path.append(p_to_src)
from src.utils import display
from src.searcher_ab_ids_hsh_q import Searcher
# from src.searcher_ab_ids_hsh import Searcher

from src.chess import Board
engine = chess.engine.SimpleEngine.popen_uci("./stockfish-5")

board = Board()
s = Searcher()
while not board.is_game_over():
    display(board)
    if board.turn == chess.WHITE:
        sc, m = s._search_at_depth(board, depth=3)
        board.push(m)
    else:
        result = engine.play(board, chess.engine.Limit(time=0.0007))
        board.push(result.move)
    # import pdb; pdb.set_trace()
engine.quit()

print(board.outcome().result())

print('PGN: ')

print(chess.pgn.Game.from_board(board))