import chess



# pices mask is an int representing a binary str of where the bishops are
# for that color - so count the 1's indicating where they are and see if we get 2
def has_two_bishops(board: chess.Board, color: chess.Color) -> bool:
    return bin(board.pieces_mask(chess.BISHOP, color)).count("1") == 2


    
