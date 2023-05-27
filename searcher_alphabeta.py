from loguru import logger

from hueristic import evaluate, MATE_VALUE
from board import BoardT, Move


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
        alpha = -float('inf')
        beta = float('inf')

        for move in board.generate_sorted_moves():
            board.push(move)
            score = -self.alphabeta(board, depth-1, -beta, -alpha)
            board.pop()
            # print('final', move, score, best)
            if score > best:
                best = score
                best_move = move
            alpha = max(score, alpha)

        assert best_move != Move.null()
        if not board.turn: # return eval from white's perspective
            best = - best
        return best, best_move

    def alphabeta(
            self, 
            board: BoardT, 
            depth: int,
            alpha: int = -float('inf'),
            beta:  int = float('inf')
        ):


        if depth == 0:
            score = evaluate(board)
            self.nodes += 1
            return score

        else:
            best = -float('inf')
            found=False
            b = beta
            x=False
            for move in board.generate_sorted_moves():
                found=True

                board.push(move)
                # prune null moves
                if depth > 3 and move == Move.null():
                    score = self.alphabeta(board, depth-2, alpha, beta)
                    print('i hoep u dont see me')
                    # if score is better for opponent, return 
                    # if 
                    # if score < beta, failed 
                else:
                    score = -self.alphabeta(board, depth-1, -beta, -alpha)
                    

                board.pop()
                best = max(best, score)
                alpha = max(score, alpha)

                if alpha >= beta:
                    # if depth == 5:
                    #     print('cutoff', alpha, beta, best)
                    return best

            if found:
                return best
            else:
                if board.is_check(): # mate
                    # return ply - MATE_VALUE, NULL_MOVE
                    return MATE_VALUE if board.turn else -MATE_VALUE,

                else:
                    return 0 # stalemate
