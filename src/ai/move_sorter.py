import chess
from typing import List, Generator, Dict
from .structs import Line

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


# todo: sort captures by winning capture vs equal capture
# killer moves?
# non captures sorted by history heuristic
# move from line in previous depth

# First: move from line in a previous depth
# Second: Checks, Captures, moves out of check, promotions
# Third: Attacks
# Fourth: 
def get_sorted_moves(board: chess.Board, best_line: Line, curdepth:int) -> List[chess.Move]:
    moves = list(board.legal_moves)
    moves_orig = moves.copy()
    
    # uses most valuable victim, least valuable attacker to score moves
    # if it gives a check, add an additional 50
    # if it mvoes out of check, add 200
    # if it's a promotion to a queen or a knight, add 60
    # if prior principal variation move, check first (10k)

    move_to_score: Dict[chess.Move, int] = {}
    def move_score(move):
        if move in move_to_score:
            return move_to_score[move]
        
        check = board.gives_check(move) * 50

        capture = 0
        if board.is_capture(move):
            if board.is_en_passant(move):
                capture = 15
            else:
                capture = MVV_LVA[board.piece_at(move.to_square).piece_type-1][board.piece_at(move.from_square).piece_type-1]
        
        out_of_check = 0
        if is_move_out_of_check(board, move):
            out_of_check = 200

        promotion = 0
        if is_good_promotion(move):
            promotion = 60
        
        prior_pv_move = 0
        # no change last time was uncommented
        # if curdepth > len(best_line) and len(best_line) > 0:
        #     assert best_line.moves[curdepth-1-len(best_line)] in moves_orig
        #     prior_pv_move = 10000

        score = check + capture + out_of_check + promotion + prior_pv_move
        return score
    
    moves.sort(key=move_score, reverse=True)

    return moves

def is_move_out_of_check(board, move):
    return board.is_check() and board.is_legal(move)

def is_good_promotion(move):
    return move.promotion is chess.QUEEN or move.promotion is chess.KNIGHT

def get_non_quiescent_moves(board: chess.Board) -> Generator[chess.Move, None, None]:
    moves =  list(board.legal_moves)
    move_to_score: Dict[chess.Move, int] = {}

    # uses most valuable victim, least valuable attacker to score moves
    # if it gives a check, add an additional 50
    # if it mvoes out of check, add 200
    # if it's a promotion to a queen or a knight, add 60
    def move_score(move):
        if move in move_to_score:
            return move_to_score[move]
        
        check = board.gives_check(move) * 50

        capture = 0
        if board.is_capture(move):
            if board.is_en_passant(move):
                capture = 15
            else:
                capture = MVV_LVA[board.piece_at(move.to_square).piece_type-1][board.piece_at(move.from_square).piece_type-1]
        
        out_of_check = 0
        if is_move_out_of_check(board, move):
            out_of_check = 200

        promotion = 0
        if is_good_promotion(move):
            promotion = 60
        
        score = check + capture + out_of_check + promotion
        move_to_score[move] = score
        return score
    
    moves.sort(key=move_score, reverse=True) # descending so high scoring moves first

    for move in moves:
        assert move in move_to_score
        if move_to_score[move] > 0:
            yield move


