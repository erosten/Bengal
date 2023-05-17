import chess
from abc import ABC, abstractclassmethod, abstractmethod
    
class Evaluation:

    @abstractmethod
    def evaluate(board: chess.Board) -> int:
        pass

    @abstractmethod
    def evaluate_explained(board: chess.Board) -> int:
        pass 

    @abstractclassmethod
    def evaluate(board: chess.Board) -> int:
        pass

    @abstractclassmethod
    def evaluate_explained(board: chess.Board) -> int:
        pass