import os
import time
from collections import defaultdict
from typing import Optional, Tuple

from chess.polyglot import open_reader
from tabulate import tabulate

from .board import BoardT, Move, MoveType, popcount
from .hueristic import EG_VALUE, MATE_VALUE, evaluate
from .utils import logger

NULL_MOVE = Move.null()


DEFAULT_BOOK_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'books/bin/M11_2.bin')
BOOK_SCORE = 1337

''' TUNE '''
DELTA_PRUNE_SAFETY_MARGIN = EG_VALUE[0] * -0.5
FUTILITY_MARGIN = 500
ZW_SEARCH_WIDTH = EG_VALUE[0]

NMP_DEPTH = 3
NMP_REDUC = 2
OPENING_BOOK = True
''' TUNE '''


def wrap_gen_insert_moves(gen, initial_moves):
    for move in initial_moves:
        if move is not None:
            yield move, MoveType.OTHER

    for move, move_type in gen:
        if move not in initial_moves:
            yield move, move_type


class Searcher:
    def __init__(self, book_path: Optional[str] = None):

        # books
        if book_path:
            self.book_op = open_reader(book_path)
        else:
            try:
                self.book_op = open_reader(DEFAULT_BOOK_PATH)
            except Exception:
                logger.warning(f'Couldnt find default opening book {DEFAULT_BOOK_PATH}, proceeding without')
                self.book_op = None

        # History Hueristic
        # 64 x 64 for from,to indices for ea color
        self.history = {
            True: [[0 for _ in range(64)] for _ in range(64)],
            False: [[0 for _ in range(64)] for _ in range(64)],
        }

        self.pos_hist = set()

    def find_move(self, board: BoardT, depth: int) -> Move:
        score = -1000
        moves = []
        for s, m in self._search_at_depth(board, depth=depth):
            if m:
                score = s
                moves = m
                if score == BOOK_SCORE:
                    print('book')
                    return score, moves
        return score, moves

    # iterative depeening on search subroutine
    # should be named _search_at_depth(s)
    def _search_at_depth(self, board: BoardT, depth: int, can_null: bool = True):
        # stats
        self.nodes = 0
        self.lmoves = 0
        self.lnodes = 0
        self.qnodes = 0
        self.ftnodes = 0
        self.ftnodes_tried = 0
        self.dtnodes = 0
        self.dtnodes_tried = 0
        self.nm = 0
        self.nbook = 0
        self.nm_tried = 0
        self.kmoves = 0
        self.kmoves_tot = 0
        self.kmoves_ill = 0
        self.pvs_research = 0

        # tt table/PV + killer/history hueristics
        self.tt_score = {}
        self.pv_length = [0 for _ in range(64)]
        self.pv_table = [[0 for _ in range(64)] for _ in range(64)]
        self.killers = defaultdict(list)

        # setting some params
        self.max_q_depth = 100
        self.max_depth = depth
        self.ids_depth = 0
        score = 0

        # Save in position history
        self.pos_hist.add(board._board_pieces_state())

        # Try to find a book move
        entry = None if not self.book_op else self.book_op.get(board)

        if OPENING_BOOK and entry:
            self.nbook += 1
            depth = -1
            yield BOOK_SCORE, [entry.move.uci()]

        for d in range(1, depth + 1):
            self.ids_depth = d
            t = time.time()

            # if depth == 1:
            score = self.pvs(board, d, can_null=can_null, ply=0)

            # # if turn is black and score is positive, means it is good for black
            # # negate it
            if not board.turn:
                score = -score
            # self.pv_length[1:] = [0 for _ in range(63)]
            # self.pv_table[1:][1:] = [[0 for _ in range(63) ] for _ in range(63)]
            t = time.time() - t
            labels = [
                'Depth (s)',
                'Nodes',
                'QNodes',
                'Null',
                'TT N/Mv',
                'TT Sz',
                'KMv Cut/Tot/Ill',
                'Futi Pr',
                'Delt Pr',
                'PV Research',
                'Best',
                'Score',
            ]
            data = [
                f'{d} ({t:.2f})s',
                self.nodes,
                self.qnodes,
                f'{self.nm}/{self.nm_tried}',
                f'{self.lnodes, self.lmoves}',
                len(self.tt_score),
                f'{self.kmoves}/{self.kmoves_tot}/{self.kmoves_ill}',
                f'{self.ftnodes}/{self.ftnodes_tried}',
                f'{self.dtnodes}/{self.dtnodes_tried}',
                self.pvs_research,
                self.pv_table[0][0],
                score,
            ]
            logger.debug(f"cur pv: {[m for m in self.pv_table[0] if m != 0]}")
            table = tabulate([data], headers=labels, tablefmt='grid')
            # Principal Variation
            self.pv = [m for m in self.pv_table[0] if m != 0]
            logger.debug('\n' + table)
            # if abs(score) > 8000:
            #     yield score, self.pv
            #     print('mate!')
            #     break
            yield score, self.pv

    def quiesce(
        self,
        board: BoardT,
        depth: int,
        alpha: int,
        beta: int,
        ply: int,
        dp: bool,  # delta prune?
    ):
        self.qnodes += 1
        stand_pat = evaluate(board, ply)

        if stand_pat >= beta:
            return stand_pat

        # can alpha be improved
        alpha = max(alpha, stand_pat)

        # default 100
        if depth == self.max_q_depth:
            return alpha

        for move, move_type in board.generate_sorted_non_qs_moves():
            # Delta pruning on capture
            if dp and move_type == MoveType.CAPTURE:
                pieceval = EG_VALUE[board.piece_type_at(move.to_square) - 1]
                self.dtnodes_tried += 1
                if stand_pat + (pieceval + DELTA_PRUNE_SAFETY_MARGIN) < alpha:
                    self.dtnodes += 1
                    continue
            board.push(move)
            score = -self.quiesce(board, depth + 1, -beta, -alpha, ply + 1, dp)
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
        next_ply = ply + 1
        while next_ply < self.pv_length[ply + 1]:
            self.pv_table[ply][next_ply] = self.pv_table[ply + 1][next_ply]
            next_ply += 1

        # adjust length
        self.pv_length[ply] = self.pv_length[ply + 1]

    def pvs(
        self,
        board: BoardT,
        depth: int,
        alpha: float = -float('inf'),
        beta: float = float('inf'),
        can_null: bool = True,
        ply: int = 0,
        update_pv=True,
    ) -> Tuple[float, Move]:
        self.nodes += 1

        z_hash = board.__hash__()
        self.pv_length[ply] = ply
        in_check = board.is_check()
        root_node = ply == 0
        pv_node = alpha != beta - ZW_SEARCH_WIDTH
        # So we know whether this is a best score node
        alpha_orig = alpha

        if not root_node:
            # Mate Distance Prune
            beta = min(beta, MATE_VALUE - ply - 1)
            alpha = max(alpha, ply - MATE_VALUE - ply)
            if alpha >= beta:
                return alpha

        # Quiesce at depth = 0
        if depth == 0:
            # only delta prune when a certain amount of pieces maybe?
            # dp = True if self.ids_depth > 2 else False
            score = self.quiesce(board, 0, alpha, beta, ply, dp=False)
            return score

        # Don't repeat positions
        if not root_node and board._board_pieces_state() in self.pos_hist:
            return 0

        # Start to generate moves
        # Moves are added FILO (First in Last out)
        # Although even last moves will go before any board generated moves
        moves_first = []
        # Killers
        if self.killers[ply]:
            if len(self.killers[ply]) >= 2:
                kmove_2 = self.killers[ply][-2]
                if board.is_legal(kmove_2):
                    self.kmoves_tot += 1
                    moves_first.append(kmove_2)
                else:
                    self.kmoves_ill += 1

            kmove = self.killers[ply][-1]
            if board.is_legal(kmove):
                self.kmoves_tot += 1
                moves_first.append(kmove)
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
            if flag == -1:
                return tt_score
            elif flag == 0:  # exact
                if tt_move != NULL_MOVE:
                    assert board.is_legal(tt_move)
                    moves_first.append(tt_move)

            elif flag == 1:  # lower bound
                if tt_score > alpha:
                    alpha = tt_score
                    # wrap gen does not handle nulls right now, so omit them
                    if update_pv and tt_move != NULL_MOVE:
                        # update_pv handles null move lower bounds
                        self.update_pv(tt_move, ply)
                        # add hash moves to move gen
                        assert board.is_legal(tt_move)
                        moves_first.append(tt_move)

            elif flag == 2:  # upper bound
                beta = min(beta, tt_score)

            if alpha >= beta:  # prune
                return tt_score

        # if we have been through at least depth=1 of IDS
        # try PV moves first
        dist_fr_root = self.ids_depth - depth
        # if there is an entry for this depth already
        if self.pv_table[0][dist_fr_root] != 0:
            if dist_fr_root == 0:  # depth = 2 root node
                last_move = Move.from_uci(self.pv_table[0][0])
            else:
                # last move on the board was the last depths PV move
                if board.move_stack[-1] == self.pv_table[0][dist_fr_root - 1]:
                    last_move = Move.from_uci(self.pv_table[0][dist_fr_root])
                else:
                    last_move = None  # last move wasnt prior PV

            if last_move is not None:
                assert board.is_legal(last_move)
                moves_first.append(last_move)

        # Null Move Pruning
        # If we are in zugzwang, this is mistake
        # so check there is at least one major piece on the board
        if (
            dist_fr_root > 0
            and depth >= NMP_DEPTH
            and can_null
            and not in_check
            and not pv_node
            and popcount(board.occupied_co[board.turn] & ~board.pawns) > 1
        ):
            self.nm_tried += 1
            board.push(NULL_MOVE)
            score = -self.pvs(
                board, depth - 1 - NMP_REDUC, -beta, -beta + ZW_SEARCH_WIDTH, False, ply + 1, update_pv=False
            )
            board.pop()

            if score >= beta:  # if not strict, illegal move in 3s mate test #17
                self.nm += 1

                if ply > 0:
                    self.tt_score[z_hash] = (depth, 1, score, NULL_MOVE)  # lower bound
                    return score

        # Did not prune, do a normal search
        found = False
        found_pv = False
        best = -float('inf')  # best score board.turn can get from this pos
        best_move = NULL_MOVE
        move_gen = board.generate_sorted_pseudo_legal_moves(self.history[board.turn])
        move_gen = board.get_legal_generator(wrap_gen_insert_moves(move_gen, moves_first))
        for move, move_type in move_gen:
            found = True
            board.push(move)

            # Futlity Pruning
            # if depth <= 2 and self.ids_depth > 3 and not in_check and not pv_node:
            #     eval = evaluate(board)
            #     self.ftnodes_tried += 1
            #     if eval - FUTILITY_MARGIN >= beta:
            #         best_move = move
            #         best = min(eval, beta)  # at some point should be eval?
            #         self.ftnodes += 1
            #         board.pop()
            #         return best

            if found_pv:
                # zero window search around pv to check if it is still pv
                score = -self.pvs(board, depth - 1, -alpha - ZW_SEARCH_WIDTH, -alpha, can_null, ply + 1, update_pv=True)
                if score > alpha and score < beta:  # check for failure high (> alpha), else keep score
                    self.pvs_research += 1
                    score = -self.pvs(board, depth - 1, -beta, -alpha, can_null, ply + 1, update_pv=True)
            else:
                score = -self.pvs(board, depth - 1, -beta, -alpha, can_null, ply + 1, update_pv=True)

            board.pop()

            if score > best:
                best = score
                best_move = move

            if score > alpha:
                alpha = score
                found_pv = True
                if update_pv:
                    self.update_pv(move, ply)

                if alpha >= beta:
                    if move in self.killers[ply]:
                        self.kmoves += 1
                    break

                # save in history
                if move_type is MoveType.CAPTURE:
                    self.history[board.turn][best_move.from_square][best_move.to_square] += 2**depth

        if found:

            # TT Management
            flag = -1
            if best >= beta:  # failed high, lower bound
                flag = 1
                # killers = non-captures that are beta-cutoffs
                if (
                    best > beta
                    and not board.is_capture(best_move)
                    and best_move is not NULL_MOVE
                    and not best_move.promotion
                ):
                    self.killers[ply].append(best_move)

            if best <= alpha_orig:  # failed low, upper bound
                flag = 2

            if alpha_orig < best and best < beta:  # exact, PV node
                flag = 0

            # if no entry or this depth is less or eq to existing
            if not self.tt_score.get(z_hash) or depth <= self.tt_score[z_hash][1]:
                self.tt_score[z_hash] = (depth, flag, best, best_move, board.copy())

            return best
        else:  # no moves
            if board.is_check():
                # + ply prioritizes shorter checkmates
                return -MATE_VALUE + ply
            else:
                return 0  # stalemate
