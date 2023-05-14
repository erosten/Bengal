import chess
from typing import List

# most valuable victim, least valuable attacker
# https://rustic-chess.org/search/ordering/mvv_lva.html#:~:text=MVV%2DLVA%20stands%20for%20Most,the%20strongest%20to%20the%20weakest.
# MVV_VLA[victim][attacker]
MVV_LVA = [
    [0, 0, 0, 0, 0, 0, 0],       # victim K, attacker K, Q, R, B, N, P, None
    [50, 51, 52, 53, 54, 55, 0], # victim Q, attacker K, Q, R, B, N, P, None
    [40, 41, 42, 43, 44, 45, 0], # victim R, attacker K, Q, R, B, N, P, None
    [30, 31, 32, 33, 34, 35, 0], # victim B, attacker K, Q, R, B, N, P, None
    [20, 21, 22, 23, 24, 25, 0], # victim N, attacker K, Q, R, B, N, P, None
    [10, 11, 12, 13, 14, 15, 0], # victim P, attacker K, Q, R, B, N, P, None
    [0, 0, 0, 0, 0, 0, 0],       # victim None, attacker K, Q, R, B, N, P, None
]


def get_sorted_moves(board: chess.Board) -> List[chess.Move]:
    moves = list(board.legal_moves)
        
    def move_score(move):
        
        check = board.gives_check(move) * 50
        capture = 0
        if board.is_capture(move):
            if board.is_en_passant(move):
                capture = 15
            else:
                capture = MVV_LVA[board.piece_at(move.to_square).piece_type-1][board.piece_at(move.from_square).piece_type-1]
        return check + capture
    
    moves.sort(key=move_score, reverse=True)

    return moves


def get_sorted_moves_only_checks_captures(board: chess.Board) -> List[chess.Move]:
    checks_and_caps = [move for move in board.legal_moves if board.gives_check(move) or board.is_capture(move)]

    def move_score(move):
        
        check = board.gives_check(move) * 50
        capture = 0
        if board.is_capture(move):
            if board.is_en_passant(move):
                capture = 15
            else:
                capture = MVV_LVA[board.piece_at(move.to_square).piece_type-1][board.piece_at(move.from_square).piece_type-1]
        return check + capture
    
    checks_and_caps.sort(key=move_score, reverse=True)

    return checks_and_caps


