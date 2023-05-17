import chess





# import pdb; pdb.set_trace()

# def get_


# based on https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function
class DynamicPST:

    # def evaluate(board):

    
    def evaluate_explained(board):

        mg = [0,0]
        eg = [0,0]
        gamePhase = 0

        pmap = board.piece_map()
        for sq, piece in pmap.items():
            c = int(not piece.color)
            pc = (piece.piece_type-1)*2 + c
            mg[piece.color] += MG_TABLE[pc][sq]
            eg[piece.color] += EG_TABLE[pc][sq]
            gamePhase += GAME_PHASE_VALUES[pc]
        
        # tapered eval
        mgScore = mg[chess.WHITE] - mg[chess.BLACK]
        egScore = eg[chess.WHITE] - eg[chess.BLACK]

        # calc phase
        mgPhase = gamePhase
        if mgPhase > 24:
            mgPhase = 24
        egPhase = 24 - mgPhase

        # calc final result from early game/mid game contributions
        eg = egPhase / 24
        mg = mgPhase / 24
        res = mgScore * mg + egScore * eg
        print(mg, mgScore, eg, egScore, res)
        return res
    


# def check_max_min_vals():
#     for 


# if __name__ == '__main__':
#     check_max_min_vals()    