from ai.evaluations.hueristic import Hueristic
from utils import display
import chess
from chess import SquareSet as ss

sep = '-'*20
f = Hueristic()
b = chess.Board(fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
c = chess.WHITE
display(b)
f.set(b)

print(f'white mobility: {len(f.mobility_area[True])}')
print(f.mobility_area[True])
print(f._mobility_mg_color(True))
print(f'black mobility: {len(f.mobility_area[False])}')
print(f.mobility_area[False])
print(f._mobility_mg_color(False))

print(sep)
print(len(f.pieces[True][chess.KNIGHT]))