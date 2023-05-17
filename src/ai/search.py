import chess
import time
from collections import defaultdict
from typing import List, Tuple, Generator
import operator
from dataclasses import dataclass

from .evaluations import get_eval_fn
from .move_sorter import get_sorted_moves, get_non_quiescent_moves
from .structs import Node, Line
from .transpositions import init_zobrist_hash, zobrist_hash


# resources:
# https://github.com/patterson-tom/Dionysus/blob/master/Dionysus/searcher.cpp
# 

def is_draw(board: chess.Board) -> bool:
    return (
        board.is_stalemate() or
        board.is_insufficient_material() or
        board.is_seventyfive_moves() or
        board.is_fivefold_repetition()
    )

class Searcher:

    def __init__(self, evaluator = 'dynamic_tricks'):
        # transposition table
        self.table = {}
        self.init_state = init_zobrist_hash(seed = 42)
        self.evaluate = get_eval_fn(evaluator)

        self.PV_TABLE = []

    # todo - implement time limit here?
    def find_move(self, board: chess.Board, depth: int) -> chess.Move:
        for ai_move, score, _ in self.iterative_depeening_search(board, depth = depth):
            ai_move = ai_move
        return ai_move
    
    # iterative depeening minimax alpha beta search
    def iterative_depeening_search(self, board: chess.Board, depth: int) -> Generator[Tuple[chess.Move, int, int], None, None]:
        time_by_depth = defaultdict(float)
        # Keep track of previously computed lines to call next
        best_line = Line()
        ## Depth = 3 --> for 1,2,3
        for d in range(1, depth+1):

            t1 = time.time()

            node, best_line = self.__search_at_depth(board.copy(), d, best_line)
            best_move, score = node.move, node.score

            # Report
            print(f'Best moves (min, d={d}) : {best_move}')
            print(f'Nodes visited: {self.nodes_visited}')
            print(f'Quiescent Nodes visited: {self.qnodes_visited}')
            print(f'Best Line: \n{best_line}')

            # print(f'Best Line (Cached: {best_line in self.lines_from_cache}): \n{best_line}')
            time_by_depth[d] = time.time() - t1

            # yield best moves as they come
            
            yield best_move, score, depth
        
        # Overally Report 
        print('Time by depth:')
        for d, t in time_by_depth.items():
            print(f'Depth {d}: {t:.3f}s')
        print(f'Nodes Cached: {len(self.table)}')
        print(f'Nodes loaded from Cache: {self.loaded_from_cache}')

    def __search_at_depth(self, board: chess.Board, depth: int, best_line: Line = Line()) -> Node:
        # reset stuff
        self.max_depth = depth
        self.nodes_visited = 0
        self.qnodes_visited = 0
        self.loaded_from_cache = 0
        self.quiesce_depth = 3
        self.maximizer = board.turn

        # for move ordering
        self.best_line = best_line
        # self.lines_from_cache = set()

        # call
        return self.minimax(board, depth, -float('inf'), float('inf'))


    def quiesce(self, board: chess.Board, alpha: int, beta: int, depth, max_node: bool) -> Node:
        self.qnodes_visited +=1
        # term is taken from the game of poker, where it denotes playing one's hand without drawing more cards
        stand_pat = self.evaluate(board)
        if depth == 0:
            return stand_pat
        
        moves = list(get_non_quiescent_moves(board))
        if not moves:
            return stand_pat
        
        if max_node:
            best_score = -float('inf')
            if stand_pat >= beta:
                return stand_pat
            if alpha < stand_pat:
                alpha = stand_pat
            
            for move in moves:
                board.push(move)
                score = self.quiesce(board, alpha, beta, depth-1, False)
                board.pop()
                best_score = max(best_score, score)
                if best_score >= beta:
                    return best_score
                alpha = max(best_score, alpha)
            return best_score
        else:
            best_score = float('inf')
            if stand_pat <= alpha:
                return stand_pat
            if stand_pat < beta:
                beta = stand_pat
            
            for move in moves:
                board.push(move)
                score = self.quiesce(board, alpha, beta, depth-1, True)
                board.pop()
                best_score = min(best_score, score)
                if best_score <= alpha:
                    return best_score
                beta = min(best_score, beta)
            return best_score


    def minimax(self, board: chess.Board, depth: int, alpha, beta) -> Tuple[Node, Line]:
        self.nodes_visited += 1

        # return from table if already seen
        # only return if the depth at which we saw it is deeper or equal
        # to the depth we're seeing it at now
        hash = zobrist_hash(board, self.init_state)
        if hash in self.table and self.table[hash]['depth'] >= depth:
            self.loaded_from_cache += 1
            # self.lines_from_cache.add(self.table[hash]['line'])
            return self.table[hash]['node'], self.table[hash]['line']
        
        # End state
        
        if depth == 0 or board.is_checkmate() or is_draw(board):
            # whether we are at a max node or not is whether board.turn == same board.turn as when minimax was first called
            score = self.quiesce(board, alpha, beta, depth = self.quiesce_depth, max_node=board.turn == self.maximizer)
            # score = self.evaluate(board)
            return Node(chess.Move.null(), score), Line()




        # Are we white or black?
        white = board.turn
        # Properly initialize score
        best_score = (((white*2)-1)*float('inf'))*-1
        # Properly initalize way to compare score
        if white:
            comparator = operator.ge
        else:
            comparator = operator.le

        # Go
        best_moves = []
        best_line = Line()
        for move in get_sorted_moves(board, self.best_line, depth):
            board.push(move)
            node, node_line = self.minimax(board,depth-1,alpha,beta)
            score = node.score
            board.pop()

            # at least gt or lt, may be eq
            if comparator(score, best_score):
                # if gt or lt
                if score != best_score:
                    best_moves.clear()
                    # reset best_line
                    best_line = Line()
                    best_line.add(move)
                    best_line.add_moves(node_line)

                # append and record
                best_score = score
                best_moves.append((move, score))
                self.record(Node(move, score), hash, depth, best_line)
    
            if white:
                alpha = max(alpha, score)
            else:
                beta = min(beta, score)
            
            if beta <= alpha:
                if len(best_moves) == 0:
                    
                    return Node(move, best_score), best_line
                break
        
        # just take first for now
        try:
            best_move, best_score = best_moves[0][0], best_moves[0][1]
        except IndexError as e:
            print('saw this error once, check to see if there are valid moves? stalemate maybe?')
            import pdb; pdb.set_trace() 
        ret_node = Node(best_move, best_score)
        self.record(ret_node, hash, depth, best_line)
        return ret_node, best_line

    def record(self, node: Node, hash: int, depth: int, line: Line) -> None:
        if hash not in self.table:
            self.table[hash] = {}
        self.table[hash]['node'] = node
        self.table[hash]['depth'] = depth
        self.table[hash]['line'] = line