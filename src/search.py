import chess
from chess.polyglot import zobrist_hash
import time
from collections import defaultdict
from typing import Tuple, Generator
import operator


from .evaluations.hueristic import evaluate, MATE_VALUE
from .move_sorter import get_non_quiescent_moves
from .board_state import BoardState
# from .structs import  Line


# resources:
# https://github.com/patterson-tom/Dionysus/blob/master/Dionysus/searcher.cpp
# 

def is_draw(board: BoardState) -> bool:
    return (
        board.is_stalemate() or
        board.is_insufficient_material() or
        board.is_seventyfive_moves() or
        board.is_fivefold_repetition()
    )

class Searcher:

    def __init__(self, evaluator = 'dynamic_tricks'):

        # transposition tables
        # hash -> (score,)
        # refreshed when searching on new position
        # for pruning tree from previously seen positions
        self.tp_score = {}

        # hash -> latest depth of score in tp_score
        self.tp_score_depths = {}

        # hash -> move
        # persists throughout positions
        # for finding killer moves?
        self.tp_move = {}

    # todo - implement time limit here?
    def find_move(self, board: BoardState, depth: int) -> chess.Move:
        for ai_move, score, _ in self.iterative_depeening_search(board, depth = depth):
            ai_move = ai_move
        return ai_move
    
    # iterative depeening minimax alpha beta search
    def iterative_depeening_search(self, board: BoardState, depth: int) -> Generator[Tuple[chess.Move, int, int], None, None]:
        time_by_depth = defaultdict(float)
    
        # self.tp_score.clear()
        h = zobrist_hash(board)
        for d in range(1, depth+1):

            t1 = time.time()

            score = self.__search_at_depth(board.copy(), d)
            best_move = self.tp_move[h]

            # Report
            print(f'Best move, score (min, d={d}) : {best_move}, {self.tp_score[h]}')
            print(f'Depth')
            print(f'Nodes visited: {self.nodes}')
            print(f'Quiescent Nodes visited: {self.qnodes}')
            print(f'Cached Nodes: {len(self.tp_score)}')
            print(f'Loaded From Cache: {self.clnodes}')
            print(f'Pruned: {self.pnodes}')
            print(f'Cached Moves: {len(self.tp_move)}')
            print(f'Moves from cache: {self.hm}')

            time_by_depth[d] = time.time() - t1
            yield best_move, score, depth
        
        print('Time by depth:')
        for d, t in time_by_depth.items():
            print(f'Depth {d}: {t:.3f}s')

    def __search_at_depth(self, board: BoardState, depth: int):
        # reset stuff
        self.max_depth = depth
        # any node, quiescent nodes, already cached nodes, loaded fr cache, pruned by alphabeta
        self.nodes = 0
        self.qnodes = 0
        self.cnodes = 0
        self.clnodes = 0
        self.pnodes = 0
        self.hm = 0
        self.max_quiesce_depth = 1 # 0 = no quiesce
        self.maximizer = board.turn

        # call
        return self.minimax(board, depth, -float('inf'), float('inf'))


    # add 1 to depth each call
    def quiesce(self, board: BoardState, alpha: int, beta: int, depth, max_node: bool):
        self.qnodes +=1

        hash = zobrist_hash(board)

        # try to look up position in table, default is +/- inf
        # depth must match
        if hash in self.tp_score and self.tp_score_depths[hash] > self.max_depth+depth:            
            score = self.tp_score[hash]
            self.clnodes +=1
            
            if max_node:
                alpha = max(alpha, score)
            else:
                beta = min(beta, score)

            if beta <= alpha:
                self.pnodes += 1
                return score
            
        # term is taken from the game of poker, where it denotes playing one's hand without drawing more cards
        stand_pat = evaluate(board)
        if depth == self.max_quiesce_depth:
            return stand_pat
        
        moves = list(get_non_quiescent_moves(board))
        if not moves:
            return stand_pat
        
        if max_node:
            best_score = -float('inf')
            # current eval better than best score for min
            # just return it
            if stand_pat >= beta:
                self.record_score(hash, best_score, self.max_depth+depth)
                return stand_pat
            
            # current eval better than best for max
            # set alpha -> current eval 
            if stand_pat > alpha:
                alpha = stand_pat
            
            for move in moves:
                board.push(move)
                score = self.quiesce(board, alpha, beta, depth+1, False)
                board.pop()
                best_score = max(best_score, score)
                # min player has refutation to our max node move
                # that is better than any other we've seen for min player
                if best_score >= beta:
                    self.record_score(hash, best_score, self.max_depth+depth)
                    self.pnodes+=1
                    return best_score
                
                alpha = max(best_score, alpha)
            
            assert best_score > -float('inf') # make sure we at least had a move here..
            # there was no amazing move for min, return our best move
            return best_score
        else:
            best_score = float('inf')

            # current eval worse than best score for max
            if stand_pat <= alpha:
                self.record_score(hash, best_score, self.max_depth+depth)
                self.pnodes+=1
                return stand_pat
            
            # current eval better for min than seen so far
            if stand_pat < beta:
                beta = stand_pat
            
            for move in moves:
                board.push(move)
                score = self.quiesce(board, alpha, beta, depth+1, True)
                board.pop()
                best_score = min(best_score, score)

                # max player did not have a refutation better than their
                # the best move they could play so far
                if best_score <= alpha:
                    self.record_score(hash, best_score, self.max_depth+depth)
                    self.pnodes+=1
                    return best_score
                
                beta = min(best_score, beta)
            return best_score


    def minimax(self, board: BoardState, depth: int, alpha, beta):
        self.nodes += 1

        # Are we white or black?
        white = board.turn
        # Properly initialize score
        best_score = (((white*2)-1)*float('inf'))*-1

        # Properly initalize way to compare score
        if white:
            comparator = operator.ge
        else:
            comparator = operator.le

        # Board state for transposition tables
        hash = zobrist_hash(board)

        # try to look up position in table, default is +/- inf
        # depth must match
        if hash in self.tp_score and self.tp_score_depths[hash] > depth:            
            score = self.tp_score[hash]
            self.clnodes +=1
            
            if white:
                alpha = max(alpha, score)
            else:
                beta = min(beta, score)
            
            # must return here, not sure why..
            if beta <= alpha:
                self.pnodes += 1
                return score

        
        # Check End state
        if depth == 0 or board.is_checkmate() or is_draw(board):
            # Quiesce at depth = 0
            # whether we are at a max node or not is whether board.turn == same board.turn as when minimax was first called
            # score = self.quiesce(board, alpha, beta, depth = 0, max_node=board.turn == self.maximizer)
            score = evaluate(board)
            self.record_score(hash, score, self.max_depth)
            return score

        # try to get a hash-move
        hash_move = self.tp_move.get(hash)
        if hash_move and self.tp_score_depths[hash] > depth:

            self.hm+=1
            board.push(hash_move)
            score = self.minimax(board, depth-1, alpha, beta)
            board.pop()          

            if white:
                alpha = max(alpha, score)
            else:
                beta = min(beta, score)
            
            if beta <= alpha:
                # self.pnodes += 1
                self.record_score(hash, best_score, self.max_depth)
                return score


        # should have at least one move, if not should be found during above check
        for move in board.generate_sorted_moves():
            board.push(move)
            score = self.minimax(board,depth-1,alpha,beta)
            board.pop()

            # at least gt or lt, may be eq
            if comparator(score, best_score):
                # append and record
                best_score = score
                self.record_move(hash, move)
                self.record_score(hash, best_score, self.max_depth)

            if white:
                alpha = max(alpha, score)
                if alpha >= MATE_VALUE:
                    return alpha
            else:
                beta = min(beta, score)
                if beta <= -MATE_VALUE:
                    return beta
            
            if beta <= alpha:
                self.pnodes += 1
                self.record_score(hash, best_score, self.max_depth)
                break

        return best_score


    def record_score(self, hash: int, s: int, d: int) -> None:
        self.tp_score[hash] = s
        self.tp_score_depths[hash] = d
    
    def record_move(self, hash: int, m: chess.Move) -> None:
        self.tp_move[hash] = m