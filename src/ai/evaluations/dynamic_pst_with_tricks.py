import chess
from .evaluation import Evaluation
from .dynamic_pst import DynamicPST

class DynamicPSTwithTricks(Evaluation):


    def evaluate(board: chess.Board):
        dynamic_pst = DynamicPST.evaluate(board)

    # def evaluate_explained(board: chess.Board):