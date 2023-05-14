from dataclasses import dataclass
from typing import List
import chess

@dataclass
class Node:
    move: chess.Move
    child_move: chess.Move
    score: int
    pv: List[chess.Move]
