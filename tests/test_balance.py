# tests the balance of the evaluation function

# play 8 games against each other, each without a different pawn
# record whether the color without the pawn wins
import sys, os

p_to_src = os.path.abspath(os.path.dirname(os.path.abspath('')))
sys.path.append(p_to_src)

import chess
from tqdm import tqdm
# from src.alphabeta_searcher import Searcher as ABSearcher
from src.searcher_ab_ids_hsh import Searcher as Searcher
from Bengal.src.board import Board
from src.utils import display

w_fens = [
    '1nbqkbnr/pppppppp/8/8/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbn1/pppppppp/8/8/8/8/P1PPPPPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/pppppppp/8/8/8/8/PP1PPPPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/pppppppp/8/8/8/8/PPP1PPPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/pppppppp/8/8/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPP1PP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPP1P/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPP1/RNBQKBNR w KQkq - 0 1',
]

b_fens= [
    '1nbqkbnr/1ppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbn1/p1pppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/pp1ppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/ppp1pppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/pppp1ppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/ppppp1pp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/pppppp1p/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/1pppppp1/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
]


w_wins = 0
draws = 0 
for fen in tqdm(w_fens):
    b = Board(fen)
    s_w = Searcher()
    s_b = Searcher()
    while not (res:= b.outcome(claim_draw=True)):
        # print(bool(b.outcome(claim_draw=True)))
        if b.turn:
            sc, m = s_w._search_at_depth(b, depth=3)
        else:
            sc, m = s_b._search_at_depth(b, depth=4)
        assert m != chess.Move.null()
        b.push(m)
    
    # res = b.outcome()
    if res.winner == chess.WHITE:
        w_wins += 1
    elif res.winner == None:
        draws += 1

print(w_wins, draws)
b_wins = 0

for fen in tqdm(b_fens):
    b = BoardState(fen)
    s_w = Searcher()
    s_b = Searcher()
    while not b.outcome(claim_draw=True):

        if b.turn:
            sc, m = s_w._search_at_depth(b, depth=4)
        else:
            sc, m = s_b._search_at_depth(b, depth=3)
        b.push(m)
    
    # res = b.outcome()
    if res.winner == chess.BLACK:
        b_wins += 1
    elif res.winner == None:
        draws += 1

print(f'White wins: {w_wins}/8')
print(f'Black wins: {b_wins}/8')
print(f'Draws {draws}/8')