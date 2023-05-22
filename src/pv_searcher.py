import chess
from chess.polyglot import zobrist_hash
import time
from collections import defaultdict
from typing import Tuple, Generator
import operator


from .hueristic import evaluate, evaluate_no_move_board
from .board_state import BoardState


# alpha beta
# + Principal Variation Search (using null windows)

class PrincipalVariationSearcher:

    def __init__(self):
        self.tp_score = {}
        self.tp_score_d = {}


    # todo - implement time limit here?
    def find_move(self, board: BoardState, depth: int) -> chess.Move:
        for ai_move, score in self.iterative_depeening_search(board, depth = depth):
            ai_move = ai_move
        return ai_move
    
    # iterative depeening minimax alpha beta search
    def iterative_depeening_search(self, board: BoardState, depth: int) -> Generator[Tuple[chess.Move, int, int], None, None]:
        time_by_depth = defaultdict(float)
    
        # self.tp_score.clear()
        h = zobrist_hash(board)
        for d in range(1, depth+1):

            t1 = time.time()

            score, move = self._search_at_depth(board.copy(), d)

            # Report
            print(f'Best move, score (min, d={d}) : {move}')
            print(f'Depth')
            print(f'Nodes visited: {self.nodes}')

            time_by_depth[d] = time.time() - t1
            yield move, score
        
        print('Time by depth:')
        for d, t in time_by_depth.items():
            print(f'Depth {d}: {t:.3f}s')

    def _search_at_depth(self, board: BoardState, depth: int):
        # reset stuff
        self.max_depth = depth
        # any node, quiescent nodes, already cached nodes, loaded fr cache, pruned by alphabeta
        self.nodes = 0
        self.maximizer = board.turn

        best_move = chess.Move.null()
        best = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        self.pv = [chess.Move.null() for _ in range(depth)]

        for move in board.generate_sorted_moves():
            board.push(move)
            score = -self.pvs(board, depth-1, board.turn, -beta, -alpha)
            if score > best:
                best = score
                best_move = move
            alpha = max(score, alpha)
            board.pop()
        if not board.turn:
            best = -best
        print(f'pv: {self.pv}')
        return best, best_move
    
    # Null Window Search
    # alpha = beta - 1
    # returns alpha or refutation score
    def nws(
            self, 
            board: BoardState, 
            depth: int,
            c: chess.Color,
            beta:  int = float('inf')
        ) -> int:

        if depth == 0:
            score = evaluate(board, self.maximizer)
            self.nodes += 1
            # return score
            if not c:
                score = -score
            return score
        else:
            for move in board.generate_sorted_moves():
                board.push(move)
                score = -self.nws(board, depth-1, not c, 1-beta)
                board.pop()

                # look for moves that invalidate
                # the principal variation
                if score >= beta:
                    break
                
            # return back alpha as best score, no refutation
            return beta - 1

    def pvs(
            self, 
            board: BoardState, 
            depth: int,
            c: chess.Color,
            alpha: int = -float('inf'),
            beta:  int = float('inf'),
        ):
        if board.is_insufficient_material() or \
            board.is_seventyfive_moves() or \
                board.is_fivefold_repetition():
            self.nodes+=1
            return 0
        elif depth == 0:
            score = evaluate(board)
            self.nodes += 1
            if not c:
                score = -score
            return score
        else:
            best = -float('inf')
            found=False
            search_pv = True
            for move in board.generate_sorted_moves():
                # print(move)
                found=True
                board.push(move)

                # first move in node, explore fully
                if search_pv:
                    score = -self.pvs(board, depth-1, not c, -beta, -alpha)
                else:                 
                    score = -self.nws(board, depth-1, not c, -alpha)
                    # # score better than current
                    # # and thought prior best score was pv, re-search
                    if alpha < score < beta:
                        score = -self.pvs(board, depth-1, c, -beta, -alpha)
                
                board.pop()
                best = max(best, score)
                if best > alpha:
                    if depth >= 1:
                        self.pv[depth] = move
                    search_pv = False
                # alpha = max(alpha, best)
                if alpha >= beta:
                    break
                


            if found:
                return best
            else:
                if not c:
                    return -evaluate_no_move_board(board)
                return evaluate_no_move_board(board)
