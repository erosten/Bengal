
from typing import Tuple
from loguru import logger
import sys
# logger.remove()
# logger.add(sys.stderr, level="SUCCESS")
from .hueristic import evaluate, MATE_VALUE
from .chess import BoardT, Move

NULL_MOVE = Move.null()


def wrap_gen_insert_move(gen, move):
    yield move
    yield from gen

class Searcher:

    def __init__(self):

        # transposition tables
        self.tt = {}
        self.killers = {}
        self.tt_score = {}
        

    def find_move(self, board: BoardT, depth: int) -> Move:
        score, move = self._search_at_depth(board, depth)
        logger.info(f'Best move, score (d={depth}) : {move}, {score}')
        logger.info(f'Nodes visited: {self.nodes}')
        logger.info(f'Moves loaded: {self.lmoves}')
        logger.info(f'Moves cached: {len(self.killers)}')
        logger.info(f'Nodes cached: {len(self.tt_score)}')
        logger.info(f'Nodes loaded: {self.lnodes}')
        return move


    # iterative depeening on search subroutine
    # should be named _search_at_depth(s)
    def _search_at_depth(self, board: BoardT, depth: int):
        self.max_depth = depth
        self.nodes = 0
        self.lmoves = 0
        self.lnodes = 0
        self.nm = 0
        self.ids_mv_hist = []
        # h = board.__hash__()
        # moves = []
        for d in range(1, depth+1):
            score, move = self.alphabeta_tt(board.copy(), d, can_null=True)
            self.ids_mv_hist.append((score,move))
            logger.debug(f'({self.nodes}, {self.nm}) -- Best move, score (d={d}) : {move}, {score}')

        logger.info(f'Best move, score (d={depth}) : {move}, {score}')
        logger.info(f'Nodes visited: {self.nodes}')
        logger.info(f'Moves loaded: {self.lmoves}')
        logger.info(f'Moves cached: {len(self.killers)}')
        logger.info(f'Nodes cached: {len(self.tt_score)}')
        logger.info(f'Nodes loaded: {self.lnodes}')
        logger.info(f'Null Move Nodes Pruned: {self.nm}')
        if not board.turn:
            score = -score
        return score, move

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

    def alphabeta_tt(
            self, 
            board: BoardT, 
            depth: int,
            alpha: int = -float('inf'), # best score ive gotten
            beta:  int = float('inf'), # best score theyve gotten
            can_null: bool = True # can make a null move?
        ) -> Tuple[float, Move]:

        z_hash = board.__hash__()

        # So we know whether this is a best score node
        alpha_orig = alpha

        # Search TT's for moves/scores
        # killer
        killer = self.killers.get(z_hash)
        if killer and killer[2] >= depth and depth != self.max_depth:
            self.lmoves += 1
            # assert self.pieces_equal(killer[3], board)
            return killer[0], killer[1]

        # scores
        entry = self.tt_score.get(z_hash)
        if entry and entry[1] >= depth and depth != self.max_depth:
            self.lnodes += 1
            score = entry[0]
            node_type = entry[2]
            if node_type == 0: # lower bound
                alpha = max(alpha, score)
            else:
                beta = min(beta, score)
            
            if alpha >= beta: # prune?
                return score, NULL_MOVE



        if depth <= 0:
            # no escape, but not checkmate or stalemate
            score = evaluate(board)
            self.nodes += 1
            return score, NULL_MOVE

        else:
            best = -float('inf') # best score i can get from this pos
            found=False
            best_move = NULL_MOVE
            in_check = board.is_check()
            # Find moves
            # move_gen = board.generate_sorted_moves()

            # Null Move pruning
            # Turn owner must have at least one major piece (non pawn)
                # move_gen = wrap_gen_insert_move(move_gen, NULL_MOVE)

            # have been through at least depth=1 of IDS
            # and are at the first iteration of the next
            # start with the move from the last iteration
            if len(self.ids_mv_hist) > 0 and depth == self.max_depth:
                last_move = self.ids_mv_hist[-1][1]
            else:
                last_move = None
                # move_gen = wrap_gen_insert_move(move_gen, self.ids_mv_hist[-1][1])

            will_null = can_null and \
                (board.occupied_co[board.turn] & ~board.pawns).bit_count() > 2 and \
                    not in_check and alpha != beta + 1
            # if will_null:
            #     move_gen = board.generate_sorted_moves_null(last_move)
            # else:
            move_gen = board.generate_sorted_moves(last_move)

            # Null Move Pruning
            # If we are in zugzwang, this is mistake
            if depth > 3 and will_null:
                board.push(NULL_MOVE)
                self.nm+=1
                score, _ = self.alphabeta_tt(board, depth-3, -beta, -beta+1, False)
                score = -score  
                board.pop()

                if score >= beta:
                    self.nm += 1

                    # record it is pruned?
                    self.tt_score[z_hash] = (score, depth, 0) # lower bound
                    return beta, NULL_MOVE
                
                # elif score <= alpha: # upper bound? -> re-search
                #     score, _ = self.alphabeta_tt(board, depth-1, -beta, -alpha, can_null)
                #     score = -score
                # else:
                alpha = max(score, alpha)

            for move in move_gen:
                found=True
                board.push(move)

                # else:
                score, _ = self.alphabeta_tt(board, depth-1, -beta, -alpha, can_null)
                score = -score

                board.pop()
                if score > best:
                    best = score
                    best_move = move


                alpha = max(score, alpha)

                if alpha >= beta:
                    break

            if found:
                
                # better than ive seen so far
                # and worse for them than theyve seen so far
                if best > alpha_orig and best < beta:
                    self.killers[z_hash] = (best, best_move, depth)
                # at least better than i've seen so far or
                if best <= alpha_orig:
                    self.tt_score[z_hash] = (best, depth, 1) # upper bound

                # worse for them than they've seen so far
                if best >= beta:
                    self.tt_score[z_hash] = (best, depth, 0) # lower bound

                return best, best_move
            else:
                if board.is_check(): # mate
                    # return ply - MATE_VALUE, NULL_MOVE
                    return MATE_VALUE if board.turn else -MATE_VALUE, NULL_MOVE

                else:
                    return 0, NULL_MOVE # stalemate

