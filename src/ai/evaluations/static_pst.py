import chess
from .definitions import P_VALS, BLACK_PIECES, WHITE_PIECES, pst



class SimpleEvaluation:
    # an evaluation function where
    # > 0 denotes advantage for white
    # < 0 denote advantage for black
    def evaluate(board):


        fen = board.fen()
        fen = fen.split(' ')[0] # just need piece placement

        # check value

        # check for mate
        is_mate = False
        mate_value = 0
        if board.is_checkmate():
            color_mod = 1 if not board.turn == chess.WHITE else -1
            mate_value = color_mod * P_VALS['K']
            is_mate = True

        # material score
        white_material = sum([P_VALS[i] for i in fen if i in WHITE_PIECES])
        black_material = sum([P_VALS[i.upper()] for i in fen if i in BLACK_PIECES])
        material_value = white_material - black_material

        # piece square table
        board_str = [c for c in str(board) if c not in ('\n', ' ')]

        white_pos_value = 0
        for piece in WHITE_PIECES:
            mask = [1 if c == piece else 0 for c in board_str]
            white_pos_value += sum(tuple(P_VALS[piece] + l*r for l,r in zip(mask, pst[piece])))


        black_pos_value = 0
        for piece in BLACK_PIECES:
            mask = [1 if c == piece else 0 for c in board_str]
            black_pos_value += sum(tuple(P_VALS[piece.upper()] + l*r for l,r in zip(mask, pst[piece.upper()])))
            # move = board.peek()

        position_value = white_pos_value - black_pos_value
        # position_value = 0
        # import pdb; pdb.set_trace()

        # if len(board.move_stack) > 0:
        #     last_move = board.peek()
        #

        final_eval = mate_value  + position_value + material_value
        return final_eval


    def evaluate_explained(board):


        fen = board.fen()
        fen = fen.split(' ')[0] # just need piece placement

        # check for mate
        is_mate = False
        mate_value = 0
        if board.is_checkmate():
            color_mod = 1 if not board.turn == chess.WHITE else -1
            mate_value = color_mod * P_VALS['K']
            is_mate = True

        # material score
        white_material = sum([P_VALS[i] for i in fen if i in WHITE_PIECES])
        black_material = sum([P_VALS[i.upper()] for i in fen if i in BLACK_PIECES])
        material_value = white_material - black_material

        # piece square table
        board_str = [c for c in str(board) if c not in ('\n', ' ')]

        white_pos_value = 0
        for piece in WHITE_PIECES:
            mask = [1 if c == piece else 0 for c in board_str]
            white_pos_value += sum(tuple(P_VALS[piece] + l*r for l,r in zip(mask, pst[piece])))


        black_pos_value = 0
        for piece in BLACK_PIECES:
            mask = [1 if c == piece else 0 for c in board_str]
            black_pos_value += sum(tuple(P_VALS[piece.upper()] + l*r for l,r in zip(mask, pst[piece.upper()])))
            # move = board.peek()

        position_value = white_pos_value - black_pos_value
        # position_value = 0
        # import pdb; pdb.set_trace()

        # if len(board.move_stack) > 0:
        #     last_move = board.peek()
        #

        final_eval = mate_value  + position_value + material_value
        print(f'mate value {mate_value} + pos val {position_value} + material val {material_value} = {final_eval}')
        return final_eval
