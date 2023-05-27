from typing import Tuple
from loguru import logger
import os, sys
from collections import defaultdict
logger.remove()
logger.add(sys.stderr, level="DEBUG")
from .hueristic import evaluate, MATE_VALUE
from .board import BoardT, Move
from chess.polyglot import open_reader
import time
from tabulate import tabulate

NULL_MOVE = Move.null()

BOOK_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'books/bin/Cerebellum_Light_Poly.bin')
BOOK_SCORE = 1337


def wrap_gen_insert_move(gen, initial_move):
    if initial_move is not None:
        yield initial_move
    for move in gen:
        if gen != initial_move:
            yield move

class Searcher:

    def __init__(self):

        # books
        self.book_op = open_reader(BOOK_PATH)


    def find_move(self, board: BoardT, depth: int) -> Move:
        score, pv = self._search_at_depth(board, depth)
        logger.info(f'PV, score (d={depth}) : {pv}, {score}')
        logger.info(f'Nodes visited: {self.nodes}')
        logger.info(f'Moves loaded: {self.lmoves}')
        logger.info(f'Moves cached: {len(self.killers)}')
        logger.info(f'Nodes cached: {len(self.tt_score)}')
        logger.info(f'Nodes loaded: {self.lnodes}')
        return pv[0]


    # iterative depeening on search subroutine
    # should be named _search_at_depth(s)
    def _search_at_depth(self,
                        board: BoardT, 
                        depth: int,
                        can_null: bool = True):
        # stats
        self.nodes = 0
        self.lmoves = 0
        self.lnodes = 0
        self.qnodes = 0
        self.nm = 0
        self.nbook = 0
        self.nm_tried=0
        self.kmoves = 0
        self.kmoves_tot = 0
        self.kmoves_ill = 0
        self.asp_research = 0

        # tt table/PV/killer moves
        self.tt_score = {}
        self.pv_length = [0 for _ in range(64)]
        self.pv_table = [[0 for _ in range(64) ] for _ in range(64)]
        self.killers = defaultdict(list)

        # setting some params
        self.max_q_depth = 100
        self.max_depth = depth
        self.ids_depth = 0
        score = 0
        
        # Try to find a book move
        entry = self.book_op.get(board)

        if entry:
            self.nbook += 1
            return BOOK_SCORE, [entry.move.uci()]
        
        for d in range(1, depth+1):
            self.ids_depth = d
            t = time.time()


            # try aspiration window around prior score
            # if depth > 1:
            #     alpha = score - 200 # pawn value
            #     beta = score + 200
            #     score, move = self.alphabeta_tt(board, d, alpha, beta, can_null, ply=0)
            
            
            # if depth == 1:
            score, move = self.alphabeta_tt(board, d, can_null=can_null, ply=0)
            # else:
            #     # we tried aspiration window
            #     if score >= beta: # increase beta 
            #         score, move = self.alphabeta_tt(board, d, alpha=alpha, can_null=can_null, ply=0)
            #         self.asp_research += 1
            #     elif score <= alpha:
            #         score, move = self.alphabeta_tt(board, d, beta=beta, can_null=can_null, ply=0)
            #         self.asp_research += 1

            # # if turn is black and score is positive, means it is good for black
            # # negate it
            if not board.turn:
                score = -score
            self.pv_length[1:] = [0 for _ in range(63)]
            self.pv_table[1:][1:] = [[0 for _ in range(63) ] for _ in range(63)]
            t = time.time() - t
            labels = [
                'Depth (s)',
                'Nodes',
                'QNodes',
                'Null',
                'TT N/Mv',
                'TT Sz',
                'KMv Cut/Tot/Ill',
                'Asp Research',
                'Best',
                'Score'
            ]
            data = [f'{d} ({t:.2f})s',
                    self.nodes,
                    self.qnodes, 
                    f'{self.nm}/{self.nm_tried}', 
                    f'{self.lnodes, self.lmoves}', 
                    len(self.tt_score), 
                    f'{self.kmoves}/{self.kmoves_tot}/{self.kmoves_ill}', 
                    self.asp_research,
                    move.uci(), 
                    score
            ]
            logger.warning(f"cur pv: {[m for m in self.pv_table[0] if m != 0]}")
            table =  tabulate(
                    [data],
                    headers = labels,
                    tablefmt = 'grid'
                )
            logger.debug('\n' + table)


        # Principal Variation
        self.pv = [m for m in self.pv_table[0] if m != 0] 
        logger.success(f'PV: {self.pv}')
        return score, self.pv

    def quiesce(
            self,
            board: BoardT,
            depth: int,
            alpha: int,
            beta: int,
            ply: int,
    ):
        stand_pat = evaluate(board, ply)
        self.qnodes += 1
        if stand_pat >= beta:
            return stand_pat
        alpha = max(alpha, stand_pat)
        if depth == self.max_q_depth:
            return alpha
        for move in board.generate_sorted_non_qs_moves():
            # assert board.is_capture(move) if not board.is_check() else board.is_legal(move)
            board.push(move)
            score = -self.quiesce(board, depth+1, -beta, -alpha, ply+1)
            board.pop()
            alpha = max(alpha, score)

            if score >= beta:
                return score
        return alpha

    def update_pv(self, move, ply):
        if move == NULL_MOVE:
            return
        
        self.pv_table[ply][ply] = move.uci()
        # copy moves from deeper ply into current plys line
        next_ply = ply+1
        while next_ply < self.pv_length[ply+1]:
            self.pv_table[ply][next_ply] = self.pv_table[ply+1][next_ply]
            next_ply+=1

        # adjust length
        self.pv_length[ply] = self.pv_length[ply+1]


    def alphabeta_tt(
            self, 
            board: BoardT, 
            depth: int,
            alpha: int = -float('inf'), # best score ive gotten
            beta:  int = float('inf'), # best score theyve gotten
            can_null: bool = True, # can make a null move?
            ply: int = 0
        ) -> Tuple[float, Move]:  
        self.nodes += 1

        z_hash = board.__hash__()
        self.pv_length[ply] = ply
        in_check = board.is_check()
        # So we know whether this is a best score node
        alpha_orig = alpha


        # Quiesce at depth = 0
        if depth == 0:                
            score = self.quiesce(board, 0, alpha, beta, ply)
            return score, NULL_MOVE


        best = -float('inf') # best score board.turn can get from this pos
        found=False
        best_move = NULL_MOVE


        # Start to generate moves
        # Moves are added FILO (First in Last out)
        # Although even last moves will go before any board generated moves
        move_gen = board.generate_sorted_moves()

        # Killers
        if self.killers[ply]:
            if len(self.killers[ply]) >= 2:
                kmove_2 = self.killers[ply][-2]
                if board.is_legal(kmove_2):
                    self.kmoves_tot += 1
                    move_gen = wrap_gen_insert_move(move_gen, kmove_2)
                else:
                    self.kmoves_ill += 1

            kmove = self.killers[ply][-1]
            if board.is_legal(kmove):
                self.kmoves_tot += 1
                move_gen = wrap_gen_insert_move(move_gen, kmove)
            else:
                self.kmoves_ill += 1
            


        # scores
        entry = self.tt_score.get(z_hash)
        tt_move = None
        if entry and entry[0] >= depth:
            self.lnodes += 1
            flag = entry[1]
            tt_score = entry[2]
            tt_move = entry[3]
            if flag == 2: # valid, fully prune
                self.lmoves+=1
                self.update_pv(tt_move, ply)
                return tt_score, tt_move
            elif flag == 0: # lower bound
                if tt_score >= alpha:
                    # update_pv handles null move lower bounds
                    self.update_pv(tt_move, ply)
                    alpha = tt_score
            elif flag == 1: # upper bound
                beta = min(beta, tt_score)
            
            
            if alpha >= beta: # prune
                return tt_score, NULL_MOVE
        
        move_gen = wrap_gen_insert_move(move_gen, tt_move)

        # if we have been through at least depth=1 of IDS
        # try PV moves first
        last_move = None
        dist_fr_root = self.ids_depth-depth
        # if there is an entry for this depth already
        if self.pv_table[0][dist_fr_root] != 0:
            if dist_fr_root == 0: # depth = 2 root node
                last_move = Move.from_uci(self.pv_table[0][0])
            else:
                # last move on the board was the last depths PV move
                if board.move_stack[-1] == self.pv_table[0][dist_fr_root-1]:
                    last_move = Move.from_uci(self.pv_table[0][dist_fr_root])
                else:
                    last_move = None # last move wasnt prior PV
            
            if last_move != None:
                try:
                    assert board.is_legal(last_move)
                except:
                    import pdb; pdb.set_trace()

        move_gen = wrap_gen_insert_move(move_gen, last_move)
        # move_gen = board.legal_moves




        # Null Move Pruning
        # If we are in zugzwang, this is mistake
        # so check there is at least one major piece on the board
        if dist_fr_root > 0 and depth > 3 and can_null and not in_check \
            and (board.occupied_co[board.turn] & ~board.pawns).bit_count() > 2:
            self.nm_tried+=1
            board.push(NULL_MOVE)
            score, _ = self.alphabeta_tt(board, depth-1-2, -beta, -beta+1, False, ply)
            score = -score  
            board.pop()

            if score >= beta:
                self.nm += 1

                if ply > 0:
                    self.tt_score[z_hash] = (depth, 0, score, NULL_MOVE) # lower bound
                    return score, NULL_MOVE

        # Did not prune, do a normal search                
        for move in move_gen:
            found=True
            board.push(move)

            score, _ = self.alphabeta_tt(board, depth-1, -beta, -alpha, can_null, ply+1)
            score = -score
            board.pop()

            if score > best:
                best = score
                best_move = move

            if score > alpha:
                alpha = score
                # keep track of pv
                self.update_pv(move, ply)

            if alpha >= beta:
                if move in self.killers[ply]:
                    self.kmoves += 1
                break

        if found:

            flag = 2 # exact
            # not as good as i've seen before
            if best <= alpha_orig:
                flag = 1 # upper bound
            
            if best >= beta:
                flag = 0 # lower bound
                if best > beta and not board.is_capture(best_move):
                    self.killers[ply].append(best_move)
            
            # if no entry or this depth is less or eq to existing
            if not self.tt_score.get(z_hash) or depth <= self.tt_score[z_hash][1]:
                self.tt_score[z_hash] = (depth, flag, best, best_move)

            return best, best_move
        else:
            if board.is_check():
                # + ply prioritizes shorter checkmates
                return -MATE_VALUE + ply, NULL_MOVE
            else:
                return 0, NULL_MOVE # stalemate


