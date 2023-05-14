import chess
import time
from collections import defaultdict
from typing import List
import operator

from .evaluations import get_eval_fn
from .sorter import get_sorted_moves, get_sorted_moves_only_checks_captures
from .node import Node
from .transpositions import init_zobrist_hash, zobrist_hash

def is_draw(board: chess.Board) -> bool:
    return (
        board.is_stalemate() or
        board.is_insufficient_material() or
        board.is_seventyfive_moves() or
        board.is_fivefold_repetition()
    )


class MiniMaxAlphaBetaSearcher:

    def __init__(self, evaluator = 'dynamic_pst'):
        # transposition table
        self.table = {}
        self.init_state = init_zobrist_hash(seed = 42)
        self.evaluate = get_eval_fn(evaluator)


    def __search(self, board: chess.Board, depth: int) -> Node:
        self.max_depth = depth
        self.nodes_visited = 0
        self.qnodes_visited = 0
        return self.minimax(board, depth, [], -float('inf'), float('inf'), qdepth=3)


    def find_move(self, board: chess.Board, depth: int) -> chess.Move:
        for ai_move, child_move,score, d, pv in self.search(board, depth = depth):
            ai_move = ai_move
        return ai_move
    
    # iterative depeening minimax alpha beta search
    def search(self, board, depth):
        time_by_depth = defaultdict(float)
        for d in range(1, depth+1):
            t1 = time.time()
            node = self.__search(board.copy(), d)
            best_move, child_move, score, pv = node.move, node.child_move, node.score, node.pv
            print(f'Best moves (min, d={d}) : {best_move}')
            print(f'Nodes visited: {self.nodes_visited}')
            print(f'Quiescent Nodes visited: {self.qnodes_visited}')
            print(f'pv {score}: {pv}')
            time_by_depth[d] = time.time() - t1
            yield best_move, child_move, score, depth, pv
        
        print('Time by depth:')
        for d, t in time_by_depth.items():
            print(f'Depth {d}: {t:.3f}s')
        print(f'Nodes Cached: {len(self.table)}')


    def quiesce(self, board: chess.Board, alpha: int, beta: int, depth) -> Node:
        self.qnodes_visited +=1
        # term is taken from the game of poker, where it denotes playing one's hand without drawing more cards
        stand_pat = self.evaluate(board) * ((board.turn*2)-1)*-1

        if depth == 0:
            # return Node(chess.Move.null(), chess.Move.null(), stand_pat, [])    
            return stand_pat
        if stand_pat >= beta:
            # return Node(chess.Move.null(), chess.Move.null(), beta, pv)    
            return beta
        
        if alpha < stand_pat:
            alpha = stand_pat
        
        # hash = zobrist_hash(board, self.init_state)
        # if hash in self.table and self.table[hash]['depth'] >= depth + self.max_depth:
        #     return self.table[hash]['node']

        for move in get_sorted_moves_only_checks_captures(board):
            assert board.gives_check(move) or board.is_capture(move)
            board.push(move)
            score = -self.quiesce(board, -beta, -alpha, depth - 1)
            board.pop()

            if score >= beta:
                # return Node(chess.Move.null(), chess.Move.null(), node.score, [])  
                return beta  
            if score > alpha:
                alpha = score
            # if node.score > alpha:
            #     alpha = node.score
        
        return alpha


            

    def minimax(self, board: chess.Board, depth: int, pv: List[chess.Move], alpha, beta, qdepth: int) -> Node:
        self.nodes_visited += 1

        # return from table if already seen
        # only return if the depth at which we saw it is deeper or equal
        # to the depth we're seeing it at now
        hash = zobrist_hash(board, self.init_state)
        if hash in self.table and self.table[hash]['depth'] >= depth:
            return self.table[hash]['node']
        
        # End state
        if depth == 0 or board.is_checkmate() or is_draw(board):
            # score = self.quiesce(board, alpha, beta, qdepth)
            score = self.evaluate(board)
            return Node(chess.Move.null(), chess.Move.null(), score, [])        

        # quiescence search
        # if depth == 1:

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
        pv_node = []
        for move in get_sorted_moves(board):
            board.push(move)
            node = self.minimax(board,depth-1,pv_node,alpha,beta,qdepth)
            score, child_move, pv_next = node.score, node.move, node.pv
            board.pop()

            # at least gt or lt, may be eq
            if comparator(score, best_score):
                # if gt or lt
                if score != best_score:
                    best_moves.clear()

                # append and record
                best_score = score
                best_moves.append((move, child_move, score, pv_next))
                self.record(Node(move, child_move, score, pv_next), hash, depth)
    
            if white:
                alpha = max(alpha, score)
            else:
                beta = min(beta, score)
            
            if beta < alpha:
                if len(best_moves) == 0:
                    return Node(move, child_move, best_score, pv_next)
                break
            
        pv_node.append(best_moves[0][0])
        pv_node.extend(best_moves[0][3])
        ret_node = Node(best_moves[0][0], best_moves[0][1], best_moves[0][2], pv_node)
        self.record(ret_node, hash, depth)
        return ret_node

    def record(self, node: Node, hash: int, depth: int) -> None:
        if hash not in self.table:
            self.table[hash] = {}
        self.table[hash]['node'] = node
        self.table[hash]['depth'] = depth