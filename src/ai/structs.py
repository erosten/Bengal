import chess


from dataclasses import dataclass
from typing import List
import chess


class Node:
    def __init__(self, move: chess.Move, score: int, is_checkmate: bool = False, is_draw: bool = False):
        self.move = move
        self.score = score
        self.is_checkmate = False
        self.is_draw = False

class Line:
    def __init__(self):
        self.moves = []
    
    def add(self, move):
        self.moves.append(move)
        
    def pop(self):
        self.moves.pop(0)
    
    def add_moves(self, line):
        for move in line.moves:
            self.add(move)

    def __repr__(self):
        return ''.join([f'{i+1}: {move.uci()}\n' for i,move in enumerate(self.moves)])

    def __len__(self):
        return len(self.moves)