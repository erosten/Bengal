from typing import Tuple
from loguru import logger
import os, sys
logger.remove()
logger.add(sys.stderr, level="DEBUG")
from .hueristic import evaluate, MATE_VALUE
from .chess import BoardT, Move
from chess.polyglot import open_reader
import time

NULL_MOVE = Move.null()

BOOK_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'books/bin/Cerebellum_Light_Poly.bin')
BOOK_SCORE = 1337
def wrap_gen_insert_move(gen, move):
    yield move
    yield from gen

class Searcher:

    def __init__(self):

        # transposition tables
        self.tt = {}
        self.killers = {}

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
        self.max_depth = depth
        self.nodes = 0
        self.lmoves = 0
        self.lnodes = 0
        self.qnodes = 0
        self.nm = 0
        self.nbook = 0
        self.tt_score = {}
        self.pv_length = [0 for _ in range(64)]
        self.pv_table = [[0 for _ in range(64) ] for _ in range(64)]
        self.nm_tried=0

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
            alpha = score - 90 # pawn value
            beta = score + 90
            score, move = self.alphabeta_tt(board, d, alpha, beta, can_null, ply=0)
            if not (score > alpha and score < beta): # re-search
                score, move = self.alphabeta_tt(board, d, can_null=can_null, ply=0)

            # # if turn is black and score is positive, means it is good for black
            # # negate it
            if not board.turn:
                score = -score

            t = time.time() - t
            logger.debug(f'({self.nodes}, {self.nm}/{self.nm_tried}, {self.lnodes, self.lmoves}, {len(self.tt_score)},  {self.nbook}) -- (Nodes, Null prun, Loaded Nodes/Moves, Cache Size, Book) -- Best move, score (d={d}, {t:.2f}s) : {move}, {score}')
            logger.warning(f"cur pv: {[m for m in self.pv_table[0] if m != 0]}")




            # if abs(score) > 8000:
            #     print('Mate!')
            #     break

            # logger.debug(self.nm_tried)
        logger.info(f'Best move, score (d={depth}) : {move}, {score}')
        logger.info(f'Nodes visited: {self.nodes}')
        logger.info(f'Moves loaded: {self.lmoves}')
        logger.info(f'Moves cached: {len(self.killers)}')
        logger.info(f'Nodes cached: {len(self.tt_score)}')
        logger.info(f'Nodes loaded: {self.lnodes}')
        logger.info(f'Null Move Nodes Pruned: {self.nm}')


        # Principal Variation
        self.pv = [m for m in self.pv_table[0] if m != 0] 
        logger.success(f'PV: {self.pv}')
        return score, self.pv

    def pieces_equal(self, b1: BoardT, b2: BoardT):
        return (
            b1.occupied == b2.occupied and
            b1.occupied_co[True] == b2.occupied_co[True] and
            b1.pawns == b2.pawns and
            b1.knights == b2.knights and
            b1.bishops == b2.bishops and
            b1.rooks == b2.rooks and
            b1.queens == b2.queens and
            b1.kings == b2.kings and
            b1.turn == b2.turn and
            b1.castling_rights == b2.castling_rights and
            b1.ep_square == b2.ep_square)


    def quiesce(
            self,
            board: BoardT,
            depth: int,
            alpha: int,
            beta: int,
            ply: int,
    ):
        stand_pat = evaluate(board, ply)
        self.nodes += 1
        if stand_pat >= beta:
            return stand_pat
        alpha = max(alpha, stand_pat)
        
        for move in board.generate_sorted_non_qs_moves():
            if board.is_check() or board.is_capture(move):
                board.push(move)
                score = -self.quiesce(board, depth+1, -beta, -alpha, ply+1)
                board.pop()
                alpha = max(alpha, score)

                if score >= beta:
                    return score
        return alpha



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

        # Search TT's for moves/scores
        # killer
        killer = self.killers.get(z_hash)
        if killer and killer[2] >= depth:
            self.lmoves += 1
            kscore = killer[0]
            kmove = killer[1]
            assert board.is_legal(kmove)

            # keep track of pv since we return early
            self.pv_table[ply][ply] = kmove.uci()

            # copy moves from deeper ply into current plys line
            next_ply = ply+1
            while next_ply < self.pv_length[ply+1]:
                self.pv_table[ply][next_ply] = self.pv_table[ply+1][next_ply]
                next_ply+=1

            # adjust length
            self.pv_length[ply] = self.pv_length[ply+1]
            return kscore, kmove

        # scores
        entry = self.tt_score.get(z_hash)
        if entry and entry[1] >= depth:
            self.lnodes += 1
            score = entry[0]
            node_type = entry[2]
            if node_type == 0: # lower bound
                alpha = max(alpha, score)
                if score > alpha:
                    alpha = score
                    assert board.is_legal(move)

                    # keep track of pv
                    self.pv_table[ply][ply] = move.uci()

                    # copy moves from deeper ply into current plys line
                    next_ply = ply+1
                    while next_ply < self.pv_length[ply+1]:
                        self.pv_table[ply][next_ply] = self.pv_table[ply+1][next_ply]
                        next_ply+=1

                    # adjust length
                    self.pv_length[ply] = self.pv_length[ply+1]
            else:
                beta = min(beta, score) # upper bound
            
            if alpha >= beta: # prune?
                return score, NULL_MOVE


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
                assert board.is_legal(last_move)

        move_gen = board.generate_sorted_moves(last_move)
        # move_gen = board.legal_moves

        # Null Move Pruning
        # If we are in zugzwang, this is mistake
        # so check there is at least one major piece on the board
        if depth > 3 and can_null and not in_check \
            and (board.occupied_co[board.turn] & ~board.pawns).bit_count() > 2:
            self.nm_tried+=1
            board.push(NULL_MOVE)
            score, _ = self.alphabeta_tt(board, depth-1-2, -beta, -beta+1, True, ply+1)
            score = -score  
            board.pop()

            if score >= beta:
                self.nm += 1

                # record it is pruned?
                # self.tt_score[z_hash] = (score, depth, 0) # lower bound
                if ply > 0:
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
                if move != NULL_MOVE:
                    self.pv_table[ply][ply] = move.uci()
                    assert board.is_legal(move)
                    # copy moves from deeper ply into current plys line
                    next_ply = ply+1
                    while next_ply < self.pv_length[ply+1]:
                        self.pv_table[ply][next_ply] = self.pv_table[ply+1][next_ply]
                        next_ply+=1

                    # adjust length
                    self.pv_length[ply] = self.pv_length[ply+1]

            if alpha >= beta:
                break

        if found:
            
            # better than ive seen so far
            # and worse for them than theyve seen so far
            if best > alpha_orig and best < beta: # exact
                if best_move != NULL_MOVE:
                    self.killers[z_hash] = (best, best_move, depth)

            # not as good as i've seen before
            if best <= alpha_orig:
                self.tt_score[z_hash] = (best, depth, 1) # upper bound

            # worse for them than they've seen so far
            if best >= beta:
                self.tt_score[z_hash] = (best, depth, 0) # lower bound

            return best, best_move
        else:
            if board.is_check():
                # + ply prioritizes shorter checkmates
                return -MATE_VALUE + ply, NULL_MOVE
            else:
                return 0, NULL_MOVE # stalemate


