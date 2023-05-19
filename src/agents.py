from abc import ABC, abstractmethod
import random

import chess

from .moves import get_random_move, get_user_move
from .search import Searcher


class Agent(ABC):
    @abstractmethod
    def get_move(self) -> str:
        pass


class RandomAgent:
    def __init__(self, seed: int = 42):
        self.seed = seed  

    def get_move(self, board: chess.Board) -> str:
        random.seed(self.seed)
        return get_random_move(board)
    

class UserAgent:
    def get_move(self, board: chess.Board) -> str:
        return get_user_move(board)


class MinMaxAlphaBetaAgent:
    def __init__(self, depth: int = 3):
        self.depth = depth
        self.searcher = Searcher()

    def get_move(self, board: chess.Board) -> str:
        ai_move = self.searcher.find_move(board, depth = self.depth)
        
        return ai_move.uci()