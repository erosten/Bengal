from loguru import logger


from .hueristic import evaluate, MATE_VALUE
from .board import BoardT, Move

NULL_MOVE = Move.null()
# minimal negamax searcher
class Searcher:

    def __init__(self):
        pass

    def find_move(self, board: BoardT, depth: int) -> Move:
        score, move = self._search_at_depth(board, depth)
        logger.info(f'Best move, score (d={depth}) : {move}, {score}')
        logger.info(f'Nodes visited: {self.nodes}')
        return move

    def _search_at_depth(self, board: BoardT, depth: int):
        # reset stuff
        self.max_depth = depth
        self.nodes = 0

        best_move = Move.null()
        best = -float('inf')

        for move in board.generate_sorted_moves():
            board.push(move)
            score = -self.negamax(board, depth-1)
            board.pop()
            # print('final', move, score, best)
            if score > best:
                best = score
                best_move = move

        assert best_move != Move.null()
        if not board.turn: # return eval from white's perspective
            best = - best
        return best, best_move

    def negamax(
            self, 
            board: BoardT, 
            depth: int,
        ):


        if depth == 0:
            score = evaluate(board)
            self.nodes += 1
            return score

        else:
            best = -float('inf')
            found=False
            for move in board.generate_sorted_moves():
                found=True

                board.push(move)
                score = -self.negamax(board, depth-1)
                    

                board.pop()
                best = max(best, score)

            if found:
                return best
            else:
                if board.is_check(): # mate
                    # return ply - MATE_VALUE, NULL_MOVE
                    return MATE_VALUE if board.turn else -MATE_VALUE

                else:
                    return 0 # stalemate
