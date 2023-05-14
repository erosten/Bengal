import chess
from abc import ABC, abstractclassmethod
    
class Evaluation:

    @abstractclassmethod
    def evaluate(board: chess.Board) -> int:
        pass

    @abstractclassmethod
    def evaluate_explained(board: chess.Board) -> int:
        pass