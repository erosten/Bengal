import random
import chess
from typing import List

# https://www.chessprogramming.org/Zobrist_Hashing
# piece types are 1,2,3,4,5,6
# piece colors are 0, 1 (black, white)
# [<first square 12 pieces>, <2nd square 12 pieces>...]
def init_zobrist_hash(seed: int = 42):
    random.seed(seed)
    # 64 x 12 for each piece on each square
    state = []
    # 1 for each piece on each square + side to move is black + castling rights + en passant files
    entries = 64*12 + 1 + 4 + 8
    for _ in range(64*12):
            state.append(random.randrange(2**64))
    
    return state

def zobrist_hash(board, init_state: List[int]) -> int:
    pieces = board.piece_map()
    hash = 0
    for square in chess.SQUARES:
         if square in pieces:
            piece = pieces[square]
            # scale typing from 1-6 to 0-5, and white to 6-12 of the 1-12 allocated
            piece_idx = piece.piece_type - 1 + piece.color * 6
            assert piece_idx >= 0 and piece_idx < 12
            # square is from 0 -> 63 
            idx = square*12 + piece_idx
            hash ^= init_state[idx]
    return hash
            