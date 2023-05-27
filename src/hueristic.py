from .board import PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
from .board import WHITE, BLACK, COLORS, PIECE_TYPES, Color
from .board import scan_reversed, square_file, square_rank
from .board import BoardT
from .board import Square, SquareSet, BB_FILES
from .board import shift_up, shift_down, shift_up_right, shift_up_left
from .board import shift_down_right, shift_down_left, shift_right, shift_left
from .piece_square_tables import MG_TABLE, EG_TABLE, MG_TABLE_W, EG_TABLE_W

# need to change later maybe
Us = 'US'
Them = 'Them'

## TUNE
MATE_VALUE = 8*1025

# p, n, b, r, q, k
MG_VALUE = [82, 337, 365, 477, 1025, 0]
EG_VALUE = [94, 281, 297, 512, 936, 0]

# p, n, b, r, q, k
GAME_PHASE_VALUES = [0,1,1,2,4,0]

ONE = "1"
## TUNE


def evaluate(board: BoardT, ply: int = 0, verbose: bool = False) -> float:
    try:
        next(board.generate_legal_moves())
    except StopIteration: # no moves
        if board.is_check():
            # + ply prioritizes shorter checkmates
            return -MATE_VALUE + ply
        else:
            return  0 # stalemate
    if board.is_insufficient_material() or \
        board.is_seventyfive_moves() or \
            board.is_fivefold_repetition():
        return 0
    # material from pieces
    occ_co_pieces = {
        True: {
            PAWN: board.occupied_co[True] & board.pawns,
            KNIGHT: board.occupied_co[True] & board.knights,
            BISHOP: board.occupied_co[True] & board.bishops,
            ROOK: board.occupied_co[True] & board.rooks,
            QUEEN: board.occupied_co[True] & board.queens,
            KING: board.occupied_co[True] & board.kings,
        },

        False: {
            PAWN: board.occupied_co[False] & board.pawns,
            KNIGHT: board.occupied_co[False] & board.knights,
            BISHOP: board.occupied_co[False] & board.bishops,
            ROOK: board.occupied_co[False] & board.rooks,
            QUEEN: board.occupied_co[False] & board.queens,
            KING: board.occupied_co[False] & board.kings,
        }
    }

    # eval 
    # material + pst scoring
    mgPhase = 0
    mg_pst = [0,0]
    eg_pst = [0,0]
    # material = [0,0]
    counts = [[],[]]
    for c in COLORS:
        for p_type in PIECE_TYPES:
            pcs = occ_co_pieces[c][p_type]
            # pcs = board.occupied_co_p[c][p_type-1]

            # get counts and increment game phase
            p_type_idx = p_type-1
            cnt = 0
            # cnt = pcs.bit_count()
            # counts[c].append(cnt)

            # pst stuff
            for pc in scan_reversed(pcs):
                cnt += 1
                # A1 in top right for python-chess
                # but A1 in bot right for PST
                if c:
                    mg_pst[c] += MG_TABLE_W[p_type_idx][pc]
                    eg_pst[c] += EG_TABLE_W[p_type_idx][pc] 
                else:
                    mg_pst[c] += MG_TABLE[p_type_idx][pc]
                    eg_pst[c] += EG_TABLE[p_type_idx][pc] 
            
            counts[c].append(cnt)
            mgPhase += cnt*GAME_PHASE_VALUES[p_type_idx]


    if mgPhase > 24:
        mgPhase = 24
    egPhase = 24 - mgPhase

    # calc final result from early game/mid game contributions
    eg = egPhase / 24
    mg = mgPhase / 24

    # finish pst
    mgScore = mg_pst[WHITE] - mg_pst[BLACK]
    egScore = eg_pst[WHITE] - eg_pst[BLACK] #endgame
    pst = mgScore * mg + egScore * eg

    # finish material
    material = [0,0]
    values = (
        MG_VALUE[PAWN-1] * mg + EG_VALUE[PAWN-1] * eg,
        MG_VALUE[KNIGHT-1] * mg + EG_VALUE[KNIGHT-1] * eg,
        MG_VALUE[BISHOP-1] * mg + EG_VALUE[BISHOP-1] * eg,
        MG_VALUE[ROOK-1] * mg + EG_VALUE[ROOK-1] * eg,
        MG_VALUE[QUEEN-1] * mg + EG_VALUE[QUEEN-1] * eg,
        MG_VALUE[KING-1] * mg + EG_VALUE[KING-1] * eg,
    )
    for i in range(6):
        material[WHITE] += counts[WHITE][i]*values[i]
        material[BLACK] += counts[BLACK][i]*values[i]
    # count of piece * tapered value of 
    # material[chess.WHITE] = sum([cnt*values[i] for i, cnt in enumerate(counts[chess.WHITE])])
    # material[chess.BLACK] = sum([cnt*values[i] for i, cnt in enumerate(counts[chess.BLACK])])
    
    material_diff = material[WHITE] - material[BLACK]

    # pawns
    # pawns_mg = _pawns_mg_color(occ_co_pieces[c][PAWN]) - _pawns_mg_color(occ_co_pieces[not c][PAWN])
    pawns_mg = 0


    score = material_diff + pst + pawns_mg
    if verbose:
        print('Material', 'PST', 'Pawns MG', 'Score')
        print(material_diff, pst, pawns_mg, score)
    return score if board.turn else -score
    # return material + pst

# stalemate or checkmate
# def evaluate_no_move_board(board: BoardT, ply: int) -> float:
#     if board.is_check():
#         return MATE_VALUE if board.turn else -MATE_VALUE
#     elif board.is_stalemate():
#         return 0
#     elif board.is_insufficient_material():
#         return 0
#     else:
#         # print('?')
#         import pdb; pdb.set_trace()
#         return -10000000000000000000000000

def evaluate_explained(board: BoardT) -> float:
    return evaluate(board, verbose=True)


# def _pawns_mg_color(pawns: int, c: Color):
#     score = 0


#     # for ranks 5,6 increased bonus for blocked pawns 
#     blocking_bonuses = [5, 8]
    
#     for sq in pawns:
#         sq_sqset = SquareSet([sq])



#         if doubled_isolated(sq, sq_sqset, c):
#             score -= 6
#         elif isolated(sq, c):
#             score -= 3
#         # elif _backward():
#         #      score -= 9
        
#         score -= doubled(sq_sqset, c) * 6
#         score += connected_bonus(sq, sq_sqset, c)
#         score -= 7 * weak_and_unopposed(sq, sq_sqset, c)

#         # add blockedstarting on 5th rank
#         if blocked(sq_sqset, c) and rank(sq, c) >= 5:
#             score += blocking_bonuses[rank(sq, c) - 5]
    
#     # if True:
#     #     print(f'pawn score contribution {c}: {score}')
#     return score


# def _doubled_isolated(sq: Square, sq_sqset: SquareSet, color: Color) -> bool:
#     return _isolated(sq, color) and _doubled(sq_sqset, color)

# def _weak_and_unopposed(sq: Square, sq_sqset: SquareSet, color: Color) -> bool:
#     if _opposed(sq_sqset, color):
#         return False

#     # is it weak?
#     # TODO: Backward?
#     # return _isolated(sq, my_pawns) or _backward()
#     return _isolated(sq, color)

# # no pawns on adjacent files     
# def _isolated(sq: Square, color: Color) -> bool:
#     mask = SquareSet(BB_FILES[square_file(sq)])

#     left = shift_left(mask)
#     right = shift_right(mask)

#     adj_file_pawns = (left | right) & pieces[color][PAWN]
#     return len(adj_file_pawns) == 0

# # In chess, an doubled pawn is a pawn which has another friendly pawn on same file but in Stockfish we attach doubled pawn penalty only for pawn which has another friendly pawn on square directly behind that pawn and is not supported.
# # From https://hxim.github.io/Stockfish-Evaluation-Guide/
# def _doubled(self, sq_sqset: SquareSet, color: Color) -> bool:

#     my_pawns = self.pieces[color][PAWN]

#     # check if any pawns directly behind
#     if color: # white
#         mask = shift_down(sq_sqset)
#     else:
#         mask = shift_up(sq_sqset)

#     pawns_right_behind = mask & my_pawns

#     if len(pawns_right_behind) == 0:
#             return False

#     # check if those pawns are supported
#     if color: # white, check down, left/right
#         mask = shift_down_left(sq_sqset) | shift_down_right(sq_sqset)
#     else: # black, check up,left/right
#         mask = shift_up_left(sq_sqset) | shift_up_right(sq_sqset)

#     support_pawns = mask & my_pawns

#     if len(support_pawns) == 0:
#             return True

#     return False

# # our own pawns are blocked
# def _blocked(sq_sqset: SquareSet, color: Color) -> bool:
#     if color: # white, blocked are things up
#         mask = shift_up(sq_sqset)
#     else: # black, blocked are things down
#         mask = shift_down(sq_sqset)

#     pawns_in_front_of_my_pawns = mask & pieces[color][PAWN]

#     assert len(pawns_in_front_of_my_pawns) <= 1
#     return len(pawns_in_front_of_my_pawns) > 0

# # cannot be safely advanced part needs attacks/moves
# def _backward() -> bool:
#     pass


#     # def weak_unopposed_pawn():
#     #      pass
#     # def blocked():
#     #      pass

# def _connected_bonus(sq: Square, sq_sqset: SquareSet, color: Color) -> int:
        

#         supp = _supported(sq_sqset, color)
#         phal = _phalanx(sq_sqset, color)

#         # connected pawns further up are more valuable
#         rank_scale = [0, 3, 4, 6, 15, 24, 48]
#         if supp or phal: # is connected
#             r = _rank(sq, color)

#             if r in (0,7): # first or last rank
#                     return 0
            
#             opp = _opposed(sq_sqset, color)
#             return rank_scale[r-1] * (2 + int(phal) - int(opp)) + 11 * supp
#         else:
#             return 0

# # has pawn of opposing color right in front of it
# def _opposed(sq_sqset: SquareSet, color: Color) -> bool:
#     if color: # white
#         mask = shift_up(sq_sqset)
#     else:
#         mask = shift_down(sq_sqset)

#     opposed = mask & pieces[not color][chess.PAWN]

#     assert len(opposed) <= 1
#     return len(opposed) == 1


# def _rank(sq: Square, color: Color) -> int:
#     if color: # white, so more rank is higher -> if sq is A8, chess.square_rank = 7 and return 7
#         return square_rank(sq)
#     else: # black, so more rank is lower -> if sq is A3, chess.square_rank = 2 and return 7 - 2 => 5
#         return 7 - square_rank(sq)

#     # 0 or 1
#     # adjacent pawns to phalanx

# def _phalanx(sq_sqset: SquareSet, color: Color) -> bool: 
#     mask = shift_left(sq_sqset) | shift_right(sq_sqset)
#     phalanx_pawns = mask & pieces[color][chess.PAWN]
#     assert len(phalanx_pawns) <= 2
#     return len(phalanx_pawns) >= 1

#     # number of pawn defenders: 0,1 or 2

# def _supported(sq_sqset: SquareSet, color: Color) -> bool:
        
#     if color: # white, check down, left/right
#         mask = shift_down_left(sq_sqset) | shift_down_right(sq_sqset)
#     else: # black, check up,left/right
#         mask = shift_up_left(sq_sqset) | shift_up_right(sq_sqset)
    
#     supp_pawns = mask & pieces[color][chess.PAWN]
#     assert len(supp_pawns) <= 2
#     return len(supp_pawns) >= 1









    
#     # entrypoint for _evaluate
#     # set board, pieces and game phase
#     # def set(self, board: chess.Board, verbose=False):
#         self.verbose = verbose

#         # why do we need to copy the board here...
#         # perhaps calls from different fns during search
#         # are reassigning board to objects somehow
#         self.board = board

#         gamePhase = 0

#         for p_type, pieces in zip(
#             chess.PIECE_TYPES,
#             [self.board.pawns, self.board.knights, self.board.bishops, self.board.rooks, self.board.kings]
#         ):
#             gamePhase += bin(pieces).count("1") * GAME_PHASE_VALUES[p_type-1]

#         # calc phase
#         mgPhase = gamePhase
#         if mgPhase > 24:
#             mgPhase = 24
#         egPhase = 24 - mgPhase

#         # calc final result from early game/mid game contributions
#         self.eg = egPhase / 24
#         self.mg = mgPhase / 24


#         # self.pieces = {
#         #     # access by color
#         #     chess.WHITE: {
#         #         chess.PAWN: self.board.pieces(chess.PAWN, chess.WHITE),
#         #         chess.KNIGHT: self.board.pieces(chess.KNIGHT, chess.WHITE),
#         #         chess.BISHOP: self.board.pieces(chess.BISHOP, chess.WHITE),
#         #         chess.ROOK: self.board.pieces(chess.ROOK, chess.WHITE),
#         #         chess.QUEEN: self.board.pieces(chess.QUEEN, chess.WHITE),
#         #         chess.KING: self.board.pieces(chess.KING, chess.WHITE)
#         #     },
#         #     chess.BLACK: {
#         #         chess.PAWN: self.board.pieces(chess.PAWN, chess.BLACK),
#         #         chess.KNIGHT: self.board.pieces(chess.KNIGHT, chess.BLACK),
#         #         chess.BISHOP: self.board.pieces(chess.BISHOP, chess.BLACK),
#         #         chess.ROOK: self.board.pieces(chess.ROOK, chess.BLACK),
#         #         chess.QUEEN: self.board.pieces(chess.QUEEN, chess.BLACK),
#         #         chess.KING: self.board.pieces(chess.KING, chess.BLACK)
#         #     }
#         # }

#         # # get all white pieces
#         # self.pieces[chess.WHITE]['all'] = SquareSet()
#         # self.pieces[chess.BLACK]['all'] = SquareSet()

#         # for c in [chess.WHITE, chess.BLACK]:
#         #     for p in chess.PIECE_TYPES:
#         #         self.pieces[c]['all'] |= self.pieces[c][p]


#         # # get all white non-pawn pieces
#         # for c in [chess.WHITE, chess.BLACK]:
#         #     self.pieces[c]['pieces'] = self.pieces[c]['all'] & ~self.pieces[c][chess.PAWN]


#         # call after pieces populated

#         # generate some helpful stuff
#         # self._generate_attack_map()

#         # # attacked by us with any piece and not defended by a pawn
#         # self.weak_enemies = {c: self.attackedBy[c]['all'] & ~self.attackedBy[not c][chess.PAWN] for c in chess.COLORS}

#         # # enemy pieces defended by a pawn or defended by at least 2 pieces (pawns incl.) and not attacked by at least two pieces
#         # self.strongly_protected_enemies = {c:self.attackedBy[not c][chess.PAWN] | (self.attackedBy2[not c]['all'] & ~self.attackedBy2[c]['all']) for c in chess.COLORS}

#         # # enemy pieces not strongly protected and attacked by us
#         # self.weak_squares = {c:self.pieces[not c]['all'] & ~self.strongly_protected_enemies[c] & self.attackedBy[c]['all'] for c in chess.COLORS}

#         # self._generate_king_rings()
#         # self._generate_mobility_area()



#         # # some squaresets
#         # self.occupied = chess.SquareSet(self.board.occupied)

#         # find the phase of the game



#     def __evaluate(self):
        
#         total_score = 0
#         # piece square table scaled by game phase
#         # dynamic_pst = self._pst_score()

#         material = self._get_raw_material_score()
#         pst = self._pst_score()
#         # midgame = self._middle_game_eval()

#         if self.verbose:
#             print(f'Midgame: {self.mg*100:.2f}%, Endgame: {self.eg*100:.2f}%')
        
#         total_score = material 
#         return total_score


    
#     def _generate_mobility_area(self):
        
#         def _mobility_area(c):
#             # pawns that are blocked
#             blocked_pawns = self.pieces[c][chess.PAWN] & down(self.pieces[c][chess.PAWN])
#             # blocked and not on first two ranks (technically 2,3 since no pawns on last rank)
#             if c:
#                 rank_mask = chess.BB_RANKS[1] | chess.BB_RANKS[2]
#             else:
#                 rank_mask = chess.BB_RANKS[6] | chess.BB_RANKS[5]
            
#             early_rank_pawns = self.pieces[c][chess.PAWN] & rank_mask
#             kings_queens = self.pieces[c][chess.QUEEN] | self.pieces[c][chess.KING]

#             if c:
#                 enemy_pawn_controlled_sqs = chess.shift_down_left(self.pieces[not c][chess.PAWN]) | chess.shift_down_right(self.pieces[not c][chess.PAWN])
#             else:
#                 enemy_pawn_controlled_sqs = chess.shift_up_left(self.pieces[not c][chess.PAWN]) | chess.shift_up_right(self.pieces[not c][chess.PAWN])

#             # pinned pieces to king
#             sqs = []
#             for p in self.pieces[c]['all']:
#                 if self.board.is_pinned(c, p):
#                     sqs.append(p)
#             pinned_sqs = SquareSet(sqs)
#             return ~(blocked_pawns | early_rank_pawns | kings_queens | enemy_pawn_controlled_sqs | pinned_sqs)             

#         self.mobility_area = {c: _mobility_area(c) for c in [chess.WHITE, chess.BLACK]}

# # variables used for eval
#     def _generate_king_rings(self):
#         def _kingring(king: SquareSet):
#             return king | chess.shift_up(king) | chess.shift_down(king) | chess.shift_left(king) | \
#                 chess.shift_right(king) | chess.shift_up_left(king) | chess.shift_up_right(king) | \
#                 chess.shift_down_left(king) | chess.shift_down_right(king)
        
#         self.kingRing = {c: _kingring(self.pieces[c][chess.KING]) for c in [chess.WHITE, chess.BLACK]}

#     def _generate_attack_map(self):

#         # by [color][piece type]
#         # all squares attacked by
#         self.attackedBy = {
#             color: {
#                 piece: chess.SquareSet() for piece in chess.PIECE_TYPES
#             } 
#             for color in [chess.WHITE, chess.BLACK]            
#         }
#         # or by [color]['all']
#         self.attackedBy[chess.WHITE]['all'] = chess.SquareSet()
#         self.attackedBy[chess.BLACK]['all'] = chess.SquareSet()

#         # attacked twice

#         self.attackedBy2 = {
#             color: {
#                 piece: chess.SquareSet() for piece in chess.PIECE_TYPES
#             } 
#             for color in [chess.WHITE, chess.BLACK]            
#         }
#         self.attackedBy2[chess.WHITE]['all'] = chess.SquareSet()
#         self.attackedBy2[chess.BLACK]['all'] = chess.SquareSet()

#         # populate all pieces for white and black
#         for sq in range(64):
#             for color in [chess.WHITE, chess.BLACK]:
#                 attackers = self.board.attackers(color, sq)
            
#                 for attacker in attackers:
#                     squares_attacked = self.board.attacks(attacker)
#                     self.attackedBy[color][self.board.piece_type_at(attacker)] |= squares_attacked
#                     self.attackedBy[color]['all'] |= squares_attacked
                
#                 # 2 or more attackers
#                 if len(attackers) > 1:
#                     for attacker in attackers:
#                         squares_attacked = self.board.attacks(attacker)
#                         self.attackedBy2[color][self.board.piece_type_at(attacker)] |= squares_attacked
#                         self.attackedBy2[color]['all'] |= squares_attacked

# # call different eval components



#     def _middle_game_eval(self) -> float:
#         score = 0
#         score += self._pawns_mg()*2.5
#         score += self._threats_mg()*2
#         score += self._pieces_mg()*2
#         # score += self._mobility_mg()
#         return score

# ### Eval subcomponents start here

# ## pawn bonuses and penalties
#     def _pawns_mg(self) -> float:

#         white_score = self._pawns_mg_color(chess.WHITE)
#         black_score = self._pawns_mg_color(chess.BLACK)
#         return white_score - black_score
    
#     def _pawns_mg_color(self, perspec: Color):
#         score = 0

#         # assign right pawns        
#         my_pawns = self.pieces[perspec][chess.PAWN]

#         # for ranks 5,6 increased bonus for blocked pawns 
#         blocking_bonuses = [5, 8]
        
#         for sq in my_pawns:
#             sq_sqset = chess.SquareSet([sq])



#             if self._doubled_isolated(sq, sq_sqset, perspec):
#                 score -= 6
#             elif self._isolated(sq, perspec):
#                 score -= 3
#             # elif _backward():
#             #      score -= 9
            
#             score -= self._doubled(sq_sqset, perspec) * 6
#             score += self._connected_bonus(sq, sq_sqset, perspec)
#             score -= 7 * self._weak_and_unopposed(sq, sq_sqset, perspec)

#             # add blockedstarting on 5th rank
#             if self._blocked(sq_sqset, perspec) and self._rank(sq, perspec) >= 5:
#                 score += blocking_bonuses[self._rank(sq, perspec) - 5]
        
#         if self.verbose:
#             print(f'pawn score contribution {perspec}: {score}')
#         return score
    
# ## threat bonuses
#     def _threats_mg(self) -> float:
#         white_score = self._threats_mg_color(chess.WHITE)
#         black_score = self._threats_mg_color(chess.BLACK)
#         return white_score - black_score

#     def _threats_mg_color(self, perspec: Color) -> float:


#         # rook returns threats for p->k 1 -> 6
#         # idx 0 is no threat
#         minor_threat_scores = [0, 3, 28, 33, 44, 40, 0]
#         rook_threat_scores = [0, 2, 19, 21, 0, 29, 0]
#         score = 0
#         for enemy in self.pieces[not perspec]['pieces']:
#             sqset = chess.SquareSet([enemy])             
#             score += 32 * self._hanging(sqset, enemy, perspec)
#             score += 24 * self._king_threats(sqset, perspec)
#             score += rook_threat_scores[self._rooks_threat(sqset, enemy, perspec)]
#             score += minor_threat_scores[self._minor_threat(sqset, enemy, perspec)]
#             score += 80 * self._threat_safe_pawns(sqset, perspec)

#         score += 7 * self._weak_queen_protection( perspec)
#         score += 3 * self._restricted(perspec)

#         for pawn in self.pieces[perspec][chess.PAWN]:
#             sqset = chess.SquareSet([pawn])
#             score += 24 * self._pawn_push_threat(sqset, perspec, self.pieces[not perspec]['pieces'])

#         if self.verbose:
#             print(f'Score from threats mid game pieces ({perspec}): {score}')

#         return score

# ## pieces bonuses and penalties
#     def _pieces_mg(self) -> float:
#         white_score = self._pieces_mg_color(chess.WHITE)
#         black_score = self._pieces_mg_color(chess.BLACK)
#         return white_score - black_score

#     def _pieces_mg_color(self, perspec: Color):
#         score = 0
#         score += self._minors_behind_pawn(perspec)
#         score += 6 * self._rook_on_queen_file(perspec)
#         score += 8 * self._rook_on_king_ring(perspec)
#         score += 12 * self._bishop_on_king_ring(perspec)

#         # no bonus, semi-open file, open file
#         open_file_rook_bonuses = [0, 10, 24]
#         for rook in self.pieces[perspec][chess.ROOK]:
#             score += open_file_rook_bonuses[self._rook_on_open_or_semi_open_file(rook, perspec)]


#         for bishop in self.pieces[perspec][chess.BISHOP]:
#             score -= 2 * self._bishop_pawns(bishop, perspec)
#             score -= 3 * self._bishop_xray_pawns(bishop, perspec) 
#         if self.verbose:
#             print(f'Score from Pieces: {perspec}: {score}')
#         return score

#     def _mobility_mg(self) -> float:
#         white_score = self._mobility_mg_color(chess.WHITE)
#         black_score = self._mobility_mg_color(chess.BLACK)
#         return white_score - black_score

#     def _mobility_mg_color(self, c:Color):
#         # bonuses
#         b = [
#             [-62,-53,-12,-4,3,13,22,28,33],
#             [-48,-20,16,26,38,51,55,63,63,68,81,81,91,98],
#             [-60,-20,2,3,3,11,22,31,40,40,41,48,57,57,62],
#             [-30,-12,-8,-9,20,23,23,35,38,53,64,65,65,66,67,67,72,72,77,79,93,108,108,108,110,114,114,116]
#         ]
#         mob = 0
#         mobility_by_piece = []
#         for p in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
#             mobility_by_piece.append(self._mobility(p,c))
#             mob += b[p-2][mobility_by_piece[-1]]

#         if self.verbose:
#             print(f'mobility bonuses: {mob}, raw mobilities: {mobility_by_piece}')
#         return mob
    
# ### Lower level logic

# ## mobility

#     def _mobility(self, p: chess.PieceType, c: Color) -> int:

#         if p is chess.BISHOP:
#             return len(self.attackedBy[c][chess.BISHOP] & self.mobility_area[c] - self.pieces[c][chess.QUEEN])
#         elif p is chess.KNIGHT:
#             return len(self.attackedBy[c][chess.KNIGHT] & self.mobility_area[c] - self.pieces[c][chess.QUEEN])
#         elif p is chess.ROOK:
#             return len(self.attackedBy[c][chess.ROOK] & self.mobility_area[c])
#         elif p is chess.QUEEN:
#             return len(self.mobility_area[c] & self.attackedBy[c][chess.QUEEN] - (self.attackedBy[not c][chess.KNIGHT] | self.attackedBy[not c][chess.BISHOP] | self.attackedBy[not c][chess.ROOK]))
#         else:
#             return 0
# ## Pawns
#     def _doubled_isolated(self, sq: chess.Square, sq_sqset: SquareSet, color: Color) -> bool:
#         return self._isolated(sq, color) and self._doubled(sq_sqset, color)

#     def _weak_and_unopposed(self, sq: chess.Square, sq_sqset: SquareSet, color: Color) -> bool:
#         if self._opposed(sq_sqset, color):
#             return False

#         # is it weak?
#         # TODO: Backward?
#         # return _isolated(sq, my_pawns) or _backward()
#         return self._isolated(sq, color)

#     # no pawns on adjacent files     
#     def _isolated(self, sq: chess.Square, color: Color) -> bool:
#         mask = chess.SquareSet(chess.BB_FILES[chess.square_file(sq)])

#         left = chess.shift_left(mask)
#         right = chess.shift_right(mask)

#         adj_file_pawns = (left | right) & self.pieces[color][chess.PAWN]
#         return len(adj_file_pawns) == 0

#     # In chess, an doubled pawn is a pawn which has another friendly pawn on same file but in Stockfish we attach doubled pawn penalty only for pawn which has another friendly pawn on square directly behind that pawn and is not supported.
#     # From https://hxim.github.io/Stockfish-Evaluation-Guide/
#     def _doubled(self, sq_sqset: SquareSet, color: Color) -> bool:

#         my_pawns = self.pieces[color][chess.PAWN]

#         # check if any pawns directly behind
#         if color: # white
#             mask = chess.shift_down(sq_sqset)
#         else:
#             mask = chess.shift_up(sq_sqset)

#         pawns_right_behind = mask & my_pawns

#         if len(pawns_right_behind) == 0:
#                 return False

#         # check if those pawns are supported
#         if color: # white, check down, left/right
#             mask = chess.shift_down_left(sq_sqset) | chess.shift_down_right(sq_sqset)
#         else: # black, check up,left/right
#             mask = chess.shift_up_left(sq_sqset) | chess.shift_up_right(sq_sqset)

#         support_pawns = mask & my_pawns

#         if len(support_pawns) == 0:
#                 return True

#         return False

#     # our own pawns are blocked
#     def _blocked(self, sq_sqset: SquareSet, color: Color) -> bool:
#         if color: # white, blocked are things up
#             mask = chess.shift_up(sq_sqset)
#         else: # black, blocked are things down
#             mask = chess.shift_down(sq_sqset)

#         pawns_in_front_of_my_pawns = mask & self.pieces[color][chess.PAWN]

#         assert len(pawns_in_front_of_my_pawns) <= 1
#         return len(pawns_in_front_of_my_pawns) > 0

#     # cannot be safely advanced part needs attacks/moves
#     def _backward() -> bool:
#         pass


#         # def weak_unopposed_pawn():
#         #      pass
#         # def blocked():
#         #      pass

#     def _connected_bonus(self, sq: chess.Square, sq_sqset: SquareSet, color: Color) -> int:
            

#             supp = self._supported(sq_sqset, color)
#             phal = self._phalanx(sq_sqset, color)

#             # connected pawns further up are more valuable
#             rank_scale = [0, 3, 4, 6, 15, 24, 48]
#             if supp or phal: # is connected
#                 r = self._rank(sq, color)

#                 if r in (0,7): # first or last rank
#                         return 0
                
#                 opp = self._opposed(sq_sqset, color)
#                 return rank_scale[r-1] * (2 + int(phal) - int(opp)) + 11 * supp
#             else:
#                 return 0

#     # has pawn of opposing color right in front of it
#     def _opposed(self, sq_sqset: SquareSet, color: Color) -> bool:
#         if color: # white
#             mask = chess.shift_up(sq_sqset)
#         else:
#             mask = chess.shift_down(sq_sqset)

#         opposed = mask & self.pieces[not color][chess.PAWN]

#         assert len(opposed) <= 1
#         return len(opposed) == 1


#     def _rank(self, sq: chess.Square, color: Color) -> int:
#         if color: # white, so more rank is higher -> if sq is A8, chess.square_rank = 7 and return 7
#             return chess.square_rank(sq)
#         else: # black, so more rank is lower -> if sq is A3, chess.square_rank = 2 and return 7 - 2 => 5
#             return 7 - chess.square_rank(sq)

#         # 0 or 1
#         # adjacent pawns to phalanx

#     def _phalanx(self, sq_sqset: SquareSet, color: Color) -> bool: 
#         mask = chess.shift_left(sq_sqset) | chess.shift_right(sq_sqset)
#         phalanx_pawns = mask & self.pieces[color][chess.PAWN]
#         assert len(phalanx_pawns) <= 2
#         return len(phalanx_pawns) >= 1

#         # number of pawn defenders: 0,1 or 2

#     def _supported(self, sq_sqset: SquareSet, color: Color) -> bool:
            
#         if color: # white, check down, left/right
#             mask = chess.shift_down_left(sq_sqset) | chess.shift_down_right(sq_sqset)
#         else: # black, check up,left/right
#             mask = chess.shift_up_left(sq_sqset) | chess.shift_up_right(sq_sqset)
        
#         supp_pawns = mask & self.pieces[color][chess.PAWN]
#         assert len(supp_pawns) <= 2
#         return len(supp_pawns) >= 1


# ## threats

#     # weak enemy not defended by opponent or non pawn weak enemies attacked twice
#     # not strongly protected, we just need 
#     def _hanging(self, enemy: SquareSet, sq: chess.Square, color: Color) -> bool:

#         enemy_pawns = self.pieces[not color][chess.PAWN]

#         # not strongly protected
#         if sq not in self.weak_enemies[color]:
#             return False

#         # if enemy is pawn
#         enemy_is_pawn = len(enemy & enemy_pawns) == 1

#         # if not pawn, 
#         if not enemy_is_pawn:
#             attackers = self.board.attackers(color, sq)
#             n_att = len(attackers)
#             defenders = len(self.board.attackers(not color, sq))
#             if n_att > defenders:
#                 return True
            
#             has_pawn_attacker = len(self.pieces[color][chess.PAWN] & attackers)
#             # if self.board.piece_at(sq) == chess.QUEEN:
#             # import pdb; pdb.set_trace()
#             # if len(enemy & self.pieces[color][chess.QUEEN]) > 0:
#             #     import pdb; pdb.set_trace()
#             if has_pawn_attacker:
#                 return True
            
#             # defended more than attacked
#             return False
        
#         # if it is, but undefended, still hanging
#         # defenders are attackers of the opposing color on the square of the enemy (opposing color)
#         defenders = len(self.board.attackers(not color, sq))
#         return defenders == 0
 
#     # if square is weak and our king is attacking that square, we have a king threat
#     def _king_threats(self, enemy: SquareSet, color: Color) -> bool:
#         assert len(enemy) == 1
#         is_weak = self.weak_enemies[color].issubset(enemy)
#         king_attacking = len(self.attackedBy[color][chess.KING] & enemy) == 1
#         return is_weak and king_attacking

#     # if we can move a pawn and threaten a non-pawn enemy piece
#     def _pawn_push_threat(self, pawn: SquareSet, color: Color, enemies: SquareSet):
#         # this means move two and threatened is 3, then right/left 1

#         if color: # white
#             # push
#             pushed = chess.shift_up(pawn)
#             mask = chess.shift_up_left(pushed) | chess.shift_up_right(pushed)
#         else:
#             pushed = chess.shift_down(pawn)
#             mask = chess.shift_down_left(pushed) | chess.shift_down_right(pushed)

#         # check if enemy has pieces there
#         enemies_attacked = len(mask & enemies)
#         assert enemies_attacked <= 2
#         if enemies_attacked == 0:
#             return 0
        
#         # enemy piece there, check if pushed square is safe
#         square_and_attacked_by_enemy = pushed & self.attackedBy[not color]['all']

#         assert len(square_and_attacked_by_enemy) <= 1
#         if len(square_and_attacked_by_enemy) == 1: # not safe
#             return 0
#         else:
#             # safe, return num enemies
#             return enemies_attacked
    
#     def _threat_safe_pawns(self, enemies: SquareSet, color: Color) -> int:
#         # // Protected or unattacked squares
#         safe = ~self.attackedBy[not color]['all'] | self.attackedBy[color]['all']
#         safe_pawns = self.pieces[color][chess.PAWN] & safe
        
#         # need way to get squares attacked by safe pawns
#         if color:
#             safe_pawns_att = chess.shift_up_left(safe_pawns) | chess.shift_up_right(safe_pawns)
#         else:
#             safe_pawns_att = chess.shift_down_left(safe_pawns) | chess.shift_down_right(safe_pawns)
        
#         return len(safe_pawns_att & enemies)

#     # bonus for restricting opp piece moves
#     def _restricted(self, color):        
#         # if defended but not strongly protected and is attacked by us
#         mask = self.attackedBy[not color]['all'] & ~self.strongly_protected_enemies[not color] & self.attackedBy[color]['all']
#         return len(mask & self.pieces[not color]['all'])
    
#     # Additional bonus if weak piece is only protected by a queen
#     # weak = enemy pieces not strongly protected and attacked by us
#     def _weak_queen_protection(self, color: Color) -> int:

#         return len(self.weak_enemies[color] & self.attackedBy[not color][chess.QUEEN] & self.pieces[not color]['all'] & ~self.pieces[not color][chess.KING])

#     ## TODO
#     # def _slider_on_queen(self):
    
#     # def _knight_on_queen(self):
#     def _get_rook_xray_mask(self, rook: int) -> SquareSet:
#         file = chess.square_file(rook)
#         rank = chess.square_rank(rook)

#         file_mask = SquareSet(chess.BB_FILES[file])
#         rank_mask = SquareSet(chess.BB_RANKS[rank])
#         return file_mask | rank_mask
    
#     def _rook_xray(self, enemy: SquareSet, color: Color) -> bool:
#         for rook in self.pieces[color][chess.ROOK]:
#             # get file idx

#             if len(enemy & self._get_rook_xray_mask(rook)) > 0:
#                 return True
#         return False
    
#     def _get_bishop_xray_mask(self, bishop: int):
#         file = chess.square_file(bishop)
#         rank = chess.square_rank(bishop)

#         x = file
#         y = rank

#         # . . . . . . 1 .
#         # . . . . . 1 . .
#         # 1 . . . 1 . . .
#         # . 1 . 1 . . . .
#         # . . . . . . . . <- x,y = (2,3) indexed @ 0
#         # . 1 . 1 . . . .
#         # 1 . . . 1 . . .
#         # . . . . . 1 . .

#         to_right = 7 - x # 5
#         to_top = 7 - y # 4
#         corner=False
#         # bot left - one is 0, other is the difference
#         ray_1_ax = 0
#         ray_1_ay = 0 
#         if x < y:
#             ray_1_ay = y - x # y=1
#         else:
#             ray_1_ax = x - y
        
#         # top right
#         ray_1_bx = 7
#         ray_1_by = 7

#         if to_right < to_top:
#             ray_1_by -= (to_top-to_right)  
#         else:
#             ray_1_bx -= to_right-to_top #x=6
        
#         # corner case top left where both ray endpoitns are becoming the top left
#         # just swap to fix (hacky)
#         # if both become bottom, corner case for bishop in bot right corner
#         # swap
#         if ray_1_ax == ray_1_bx and ray_1_ay == ray_1_by:
#             corner = True
#             ray_1_ax, ray_1_ay = ray_1_ay, ray_1_ax
        
#         # from (0,1) to (6,7)
#         mask_1 = SquareSet.ray(chess.square(ray_1_ax, ray_1_ay), chess.square(ray_1_bx, ray_1_by))
#         # import pdb; pdb.set_trace()
#         try:
#             assert len(mask_1) <= 8 and len(mask_1) > 0
#         except Exception as e:
#             import pdb; pdb.set_trace()

#         # top left
#         ray_2_ax = 0 
#         ray_2_ay = 7
#         if x < to_top:
#             ray_2_ay = x+y
#         else:
#             ray_2_ax = x-to_top
        
#         # bot right

#         ray_2_bx = 7
#         ray_2_by = 7
#         if y < to_right:
#             ray_2_bx -= (to_right-y)
#             ray_2_by = 0
#         else:
#             ray_2_by = y-(to_right)
#             ray_2_bx = 7

#         # corner case bot left where both ray endpoitns are becoming the bot left

#         if ray_2_ax == ray_2_bx == 0 and ray_2_ay == ray_2_by == 0:
#             corner = True
#             ray_2_ax, ray_2_ay = 7,7
        
#         # just swap to fix (hacky)
#         # top right for when bishop in top right, swap
#         if ray_2_ax == ray_2_bx == 7 and ray_2_ay == ray_2_by == 7:
#             corner = True
#             ray_2_ax, ray_2_ay = 0,0

#         # from (0,1) to (6,7)
#         mask_2 = SquareSet.ray(chess.square(ray_2_ax, ray_2_ay), chess.square(ray_2_bx, ray_2_by))
#         try:
#             assert len(mask_2) <= 8 and len(mask_2) > 0
#         except:
#             import pdb; pdb.set_trace()

#         mask = mask_1 | mask_2
#         # if corner:
#         #     print(mask)
#         return mask

#     def _bishop_xray(self, enemy: SquareSet, color: Color) -> bool:
#         for bishop in self.pieces[color][chess.BISHOP]:
#             mask = self._get_bishop_xray_mask(bishop)
#             if len(enemy & mask) > 0:
#                 return True
#         return False

#     def _rooks_threat(self, enemy: SquareSet, enemy_sq: chess.Square, color: Color) -> int:
#         if len(enemy & self.attackedBy[color][chess.ROOK]) > 0:
#             if self.board.piece_type_at(enemy_sq) == None:
#                 import pdb; pdb.set_trace()
#             return self.board.piece_type_at(enemy_sq) # 1-6
#         elif self._rook_xray(enemy, color):
#             if self.board.piece_type_at(enemy_sq) == None:
#                 import pdb; pdb.set_trace()
#             return self.board.piece_type_at(enemy_sq)
#         return 0

#     def _minor_threat(self, enemy: SquareSet, enemy_sq: chess.Square, color: Color) -> int:
#         if len(enemy & (self.attackedBy[color][chess.KNIGHT] | self.attackedBy[color][chess.BISHOP])) > 0:
#             return self.board.piece_type_at(enemy_sq) # 1-6
#         elif self._bishop_xray(enemy, color):
#             return self.board.piece_type_at(enemy_sq) # 1-6
#         return 0

# ## pieces
#     def _minors_behind_pawn(self, color: Color) -> int:
#         minors = self.pieces[color][chess.BISHOP] | self.pieces[color][chess.KNIGHT]
#         pawns = self.pieces[color][chess.PAWN]
#         if color: 
#             minors = chess.shift_up(minors)
#         else:
#             minors = chess.shift_down(minors)
#         return len(pawns & minors)
    
#     def _outpost_total(self) -> int:
#         pass

#     # Number of pawns on the same color square as the bishop multiplied by one plus the number of our blocked pawns in the center files C, D, E or F.
#     # penalty for having bishop pawns

#     ## // Penalty according to the number of our pawns on the same color square as the
#     # // bishop, bigger when the center files are blocked with pawns and smaller
#     # // when the bishop is outside the pawn chain.
#     def _bishop_pawns(self, bishop: int, color: Color) -> int:
#         pawns = self.pieces[color][chess.PAWN]
#         light = SquareSet(chess.BB_LIGHT_SQUARES)
#         dark = SquareSet(chess.BB_DARK_SQUARES)
#         if bishop in light:
#             bishop_pawns = light & pawns
#         elif bishop in dark:
#             bishop_pawns = dark & pawns
#         else:
#             print('where is the bishop?')
        
#         n_bishop_pawns = len(bishop_pawns)
        
#         center_pawns = pawns & (chess.BB_FILE_C | chess.BB_FILE_D | chess.BB_FILE_E | chess.BB_FILE_F)

#         # blocked if enemy piece on top of advanced pawns
#         if color:
#             center_pawns = chess.shift_up(center_pawns)
#         else:
#             center_pawns = chess.shift_down(center_pawns)

#         blocked = len(center_pawns & self.pieces[not color]['all'])

#         outside_chain = bishop not in self.attackedBy[color][chess.PAWN]
#         # more penalty when in the pain chain
#         return n_bishop_pawns * (blocked+(0 if outside_chain else 1))

#     # Penalty for all enemy pawns xrayed by our bishop.
#     def _bishop_xray_pawns(self, bishop: int, color: Color) -> int:
#         xray_mask = self._get_bishop_xray_mask(bishop)
#         return len(self.pieces[not color][chess.PAWN] & xray_mask)

#     # simple bonus for a rook that is on the same file as any queen.
#     def _rook_on_queen_file(self, color: Color) -> bool:
#         queens = self.pieces[color][chess.QUEEN]
#         files = SquareSet()
#         for queen in queens:
#             files |= chess.BB_FILES[chess.square_file(queen)]

#         return len(files & self.pieces[color][chess.ROOK]) > 0
        
    
#     def _rook_on_king_ring(self, color: Color) -> bool:
#         return self._rook_xray(self.kingRing[not color], color)

#     def _bishop_on_king_ring(self, color: Color) -> bool:
#         return self._bishop_xray(self.kingRing[not color], color)

#     def _rook_on_open_or_semi_open_file(self, rook: int, color: Color) -> int:
#         file_bb = SquareSet(chess.BB_FILES[chess.square_file(rook)])

#         same_file_pawns = file_bb & self.pieces[color][chess.PAWN]
#         # import pdb; pdb.set_trace()
#         # print('same file pawns')
#         # print(same_file_pawns)
#         # print(f'file {chess.square_file(rook)}--\n')
#         # print(file_bb)
#         if len(same_file_pawns) != 0:
#             return 0
        
#         same_file_enemy_pawns = file_bb & self.pieces[not color][chess.PAWN]
#         is_semi_open = len(same_file_enemy_pawns) > 0
#         if is_semi_open:
#             return 1
        
#         return 2
   
#     # def _trapped_rook(self, rook) -> bool:
#     #     if self._rook_on_open_or_semi_open_file(rook):
#     #         return False
        
#     #     if self._mobility() > 3:
#     #         return False
        

#     def _weak_queen(self) -> int:
#         pass

#     def _queen_infiltration(self) -> int:
#         pass

#     def _long_diagonal_bishop(self) -> bool:
#         pass

#     def _king_protector(self) -> bool:
#         pass
