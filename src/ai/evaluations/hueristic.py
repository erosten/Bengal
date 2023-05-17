import chess
from chess import SquareSet, Color
from chess import shift_up as up
from chess import shift_down as down
from .evaluation import Evaluation
from .piece_square_tables import MG_TABLE, EG_TABLE, FLIP


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

# BISHOP_PAIR_BONUS = 
## TUNE
    #  << " Contributing terms for the classical eval:\n"
    #  << "+------------+-------------+-------------+-------------+\n"
    #  << "|    Term    |    White    |    Black    |    Total    |\n"
    #  << "|            |   MG    EG  |   MG    EG  |   MG    EG  |\n"
    #  << "+------------+-------------+-------------+-------------+\n"
    #  << "|   Material | " << Term(MATERIAL)
    #  << "|  Imbalance | " << Term(IMBALANCE)
    #  << "|      Pawns | " << Term(PAWN)
    #  << "|    Knights | " << Term(KNIGHT)
    #  << "|    Bishops | " << Term(BISHOP)
    #  << "|      Rooks | " << Term(ROOK)
    #  << "|     Queens | " << Term(QUEEN)
    #  << "|   Mobility | " << Term(MOBILITY)
    #  << "|King safety | " << Term(KING)
    #  << "|    Threats | " << Term(THREAT)
    #  << "|     Passed | " << Term(PASSED)
    #  << "|      Space | " << Term(SPACE)
    #  << "|   Winnable | " << Term(WINNABLE)
    #  << "+------------+-------------+-------------+-------------+\n"
    #  << "|      Total | " << Term(TOTAL)
    #  << "+------------+-------------+-------------+-------------+\n";
# pices mask is an int representing a binary str of where the bishops are
# for that color - so count the 1's indicating where they are and see if we get 2
def has_two_bishops(board: chess.Board, color: Color) -> bool:
    return bin(board.pieces_mask(chess.BISHOP, color)).count("1") == 2


def is_draw(board: chess.Board) -> bool:
    return (
        board.is_stalemate() or
        board.is_insufficient_material() or
        board.is_seventyfive_moves() or
        board.is_fivefold_repetition()
    )

# Meant for quiet positions 
class Hueristic(Evaluation):
    def __init__(self):

        # push a pawn
        self.pawn_push = {
            chess.WHITE: up,
            chess.BLACK: down
        }

    def evaluate(self, board: chess.Board, verbose=False):
        self.set(board)
        return self._evaluate(board, verbose)

    def evaluate_explained(self, board: chess.Board):
        return self.evaluate(board, verbose=True)
    
    # entrypoint for _evaluate
    # set board, pieces and game phase
    def set(self, board: chess.Board, verbose=False):
        self.verbose = verbose

        white = ((board.turn*2)-1)*-1 # if whites turn, +1, if blacks turn, -1

        # checkmate checker
        if board.is_checkmate():
            return board.is_checkmate() * -MATE_VALUE * white
        
        # draw checker
        elif is_draw(board):
            return 0

        self.board = board

        self.pieces = {
            # access by color
            chess.WHITE: {
                chess.PAWN: board.pieces(chess.PAWN, chess.WHITE),
                chess.KNIGHT: board.pieces(chess.KNIGHT, chess.WHITE),
                chess.BISHOP: board.pieces(chess.BISHOP, chess.WHITE),
                chess.ROOK: board.pieces(chess.ROOK, chess.WHITE),
                chess.QUEEN: board.pieces(chess.QUEEN, chess.WHITE),
                chess.KING: board.pieces(chess.KING, chess.WHITE)
            },
            chess.BLACK: {
                chess.PAWN: board.pieces(chess.PAWN, chess.BLACK),
                chess.KNIGHT: board.pieces(chess.KNIGHT, chess.BLACK),
                chess.BISHOP: board.pieces(chess.BISHOP, chess.BLACK),
                chess.ROOK: board.pieces(chess.ROOK, chess.BLACK),
                chess.QUEEN: board.pieces(chess.QUEEN, chess.BLACK),
                chess.KING: board.pieces(chess.KING, chess.BLACK)
            }
        }

        # get all white pieces
        self.pieces[chess.WHITE]['all'] = SquareSet()
        self.pieces[chess.BLACK]['all'] = SquareSet()

        for c in [chess.WHITE, chess.BLACK]:
            for p in chess.PIECE_TYPES:
                self.pieces[c]['all'] |= self.pieces[c][p]


        # get all white non-pawn pieces
        for c in [chess.WHITE, chess.BLACK]:
            self.pieces[c]['pieces'] = self.pieces[c]['all'] & ~self.pieces[c][chess.PAWN]


        # call after pieces populated

        # generate some helpful stuff
        self._generate_attack_map()

        # attacked by us with any piece and not defended by a pawn
        self.weak_enemies = {c: self.attackedBy[c]['all'] & ~self.attackedBy[not c][chess.PAWN] for c in chess.COLORS}

        # enemy pieces defended by a pawn or defended by at least 2 pieces (pawns incl.) and not attacked by at least two pieces
        self.strongly_protected_enemies = {c:self.attackedBy[not c][chess.PAWN] | (self.attackedBy2[not c]['all'] & ~self.attackedBy2[c]['all']) for c in chess.COLORS}

        # enemy pieces not strongly protected and attacked by us
        self.weak_squares = {c:self.pieces[not c]['all'] & ~self.strongly_protected_enemies[c] & self.attackedBy[c]['all'] for c in chess.COLORS}
        # import pdb; pdb.set_trace()
        self._generate_king_rings()
        

        self._generate_mobility_area()



        # some squaresets
        self.occupied = chess.SquareSet(self.board.occupied)

        # find the phase of the game
        gamePhase = 0

        for piece in chess.PIECE_TYPES:
            n_pieces = len(self.pieces[chess.WHITE][piece] | self.pieces[chess.BLACK][piece])
            gamePhase += n_pieces * GAME_PHASE_VALUES[piece-1]

        # calc phase
        mgPhase = gamePhase
        if mgPhase > 24:
            mgPhase = 24
        egPhase = 24 - mgPhase

        # calc final result from early game/mid game contributions
        self.eg = egPhase / 24
        self.mg = mgPhase / 24

    
    def _generate_mobility_area(self):
        
        def _mobility_area(self, c):
            # pawns that are blocked
            blocked_pawns = self.pieces[c][chess.PAWN] & down(self.pieces[c][chess.PAWN])
            # blocked and not on first two ranks (technically 2,3 since no pawns on last rank)
            if c:
                rank_mask = chess.BB_RANKS[1] | chess.BB_RANKS[2]
            else:
                rank_mask = chess.BB_RANKS[6] | chess.BB_RANKS[5]
            
            kings_queens = chess.pieces[c][chess.QUEEN] | chess.pieces[c][chess.KING]




    def _generate_king_rings(self):
        def _kingring(king: SquareSet):
            return king | chess.shift_up(king) | chess.shift_down(king) | chess.shift_left(king) | \
                chess.shift_right(king) | chess.shift_up_left(king) | chess.shift_up_right(king) | \
                chess.shift_down_left(king) | chess.shift_down_right(king)
        
        self.kingRing = {c: _kingring(self.pieces[c][chess.KING]) for c in [chess.WHITE, chess.BLACK]}

    def _generate_attack_map(self):

        # by [color][piece type]
        # all squares attacked by
        self.attackedBy = {
            color: {
                piece: chess.SquareSet() for piece in chess.PIECE_TYPES
            } 
            for color in [chess.WHITE, chess.BLACK]            
        }
        # or by [color]['all']
        self.attackedBy[chess.WHITE]['all'] = chess.SquareSet()
        self.attackedBy[chess.BLACK]['all'] = chess.SquareSet()

        # attacked twice

        self.attackedBy2 = {
            color: {
                piece: chess.SquareSet() for piece in chess.PIECE_TYPES
            } 
            for color in [chess.WHITE, chess.BLACK]            
        }
        self.attackedBy2[chess.WHITE]['all'] = chess.SquareSet()
        self.attackedBy2[chess.BLACK]['all'] = chess.SquareSet()

        # populate all pieces for white and black
        for sq in range(64):
            for color in [chess.WHITE, chess.BLACK]:
                attackers = self.board.attackers(color, sq)
            
                for attacker in attackers:
                    squares_attacked = self.board.attacks(attacker)
                    self.attackedBy[color][self.board.piece_type_at(attacker)] |= squares_attacked
                    self.attackedBy[color]['all'] |= squares_attacked
                
                # 2 or more attackers
                if len(attackers) > 1:
                    for attacker in attackers:
                        squares_attacked = self.board.attacks(attacker)
                        self.attackedBy2[color][self.board.piece_type_at(attacker)] |= squares_attacked
                        self.attackedBy2[color]['all'] |= squares_attacked


        

        
        self.mobilityArea = {}


    def _evaluate(self, board: chess.Board, verbose=False):
        total_score = 0
        # piece square table scaled by game phase
        dynamic_pst = self._pst_score()

        material = self._get_raw_material_score()

        midgame = self._middle_game_eval()
        # import pdb; pdb.set_trace()
        structure = 0
        # bonus for two bishops
        # bishop_pair_bonus = (len(self.white_bishops) >= 2)*bishop_value*0.1 - (len(self.black_bishops) >=2)*bishop_value*0.1
        # import pdb; pdb.set_trace()
        # score = dynamic_pst + material + bishop_pair_bonus

        
        # # pawn structure
        # pawn_score = pawns_midgame(white_pawns, black_pawns, pawn_value)
        # # white_pawns_iso = isolated_pawns(white_pawns)
        # # black_pawns_iso = isolated_pawns(black_pawns)



        # import pdb; pdb.set_trace()
        if verbose:
            print(f'Midgame: {self.mg*100:.2f}%, Endgame: {self.eg*100:.2f}%')
            # print(f'Dynamic PST: {dynamic_pst} + material {material} + bishop pair {bishop_pair_bonus} = {score}')
        
        total_score = dynamic_pst + material + midgame
        return total_score



    def _pst_score(self) -> int:

            mg = [0,0]
            eg = [0,0]

            pmap = self.board.piece_map()
            for sq, piece in pmap.items():
                # in above, when sq is 0 it hsould be A8, 
                # when sq is 7 it should be h8
                # when sq is 56, it should be A1
                # when sq is 63, it should be h1
                # need to convert..
                
                c = int(piece.color)
                if piece.color:
                    sq = FLIP(sq)
                pc = (piece.piece_type-1)*2 + c
                mg[piece.color] += MG_TABLE[pc][sq]
                eg[piece.color] += EG_TABLE[pc][sq]
            
            # tapered eval
            mgScore = mg[chess.WHITE] - mg[chess.BLACK]
            egScore = eg[chess.WHITE] - eg[chess.BLACK] #endgame

            res = mgScore * self.mg + egScore * self.eg
            return res

    def _get_raw_material_score(self) -> int:

        def value(piece: chess.PIECE_TYPES):
            return MG_VALUE[piece-1] * self.mg + EG_VALUE[piece-1] * self.eg
        
        # material value scaled by game phase
        values = [
            value(chess.PAWN),
            value(chess.KNIGHT),
            value(chess.BISHOP),
            value(chess.ROOK),
            value(chess.QUEEN),
            value(chess.KING),
        ]

        white_material = 0
        for key, value in zip(chess.PIECE_TYPES, values):
            white_material += value*len(self.pieces[chess.WHITE][key])


        black_material = 0
        for key, value in zip(chess.PIECE_TYPES, values):
            black_material += value*len(self.pieces[chess.BLACK][key])

        # total raw material difference
        return white_material - black_material

    def _middle_game_eval(self) -> float:
        score = 0
        score += self._pawns_mg()*2.5
        score += self._threats_mg()*2
        score += self._pieces_mg()*2
        return score

### Callers

## pawns
    def _pawns_mg(self) -> float:

        white_score = self._pawns_mg_color(chess.WHITE)
        black_score = self._pawns_mg_color(chess.BLACK)
        return white_score - black_score
    
    def _pawns_mg_color(self, perspec = Color):
        score = 0

        # assign right pawns        
        my_pawns = self.pieces[perspec][chess.PAWN]

        # for ranks 5,6 increased bonus for blocked pawns 
        blocking_bonuses = [5, 8]
        
        for sq in my_pawns:
            sq_sqset = chess.SquareSet([sq])



            if self._doubled_isolated(sq, sq_sqset, perspec):
                score -= 6
            elif self._isolated(sq, perspec):
                score -= 3
            # elif _backward():
            #      score -= 9
            
            score -= self._doubled(sq_sqset, perspec) * 6
            score += self._connected_bonus(sq, sq_sqset, perspec)
            score -= 7 * self._weak_and_unopposed(sq, sq_sqset, perspec)

            # add blockedstarting on 5th rank
            if self._blocked(sq_sqset, perspec) and self._rank(sq, perspec) >= 5:
                score += blocking_bonuses[self._rank(sq, perspec) - 5]
        
        if self.verbose:
            print(f'pawn score contribution {perspec}: {score}')
        return score
    
## threats
    def _threats_mg(self) -> float:
        white_score = self._threats_mg_color(chess.WHITE)
        black_score = self._threats_mg_color(chess.BLACK)
        return white_score - black_score

    def _threats_mg_color(self, perspec: Color) -> float:


        # rook returns threats for p->k 1 -> 6
        # idx 0 is no threat
        minor_threat_scores = [0, 3, 28, 33, 44, 40, 0]
        rook_threat_scores = [0, 2, 19, 21, 0, 29, 0]
        score = 0
        for enemy in self.pieces[not perspec]['pieces']:
            sqset = chess.SquareSet([enemy])             
            score += 32 * self._hanging(sqset, enemy, perspec)
            score += 24 * self._king_threats(sqset, enemy, perspec)
            score += rook_threat_scores[self._rooks_threat(sqset, enemy, perspec)]
            score += minor_threat_scores[self._minor_threat(sqset, enemy, perspec)]
            score += 7 * self._weak_queen_protection(sqset, perspec)
        score += 3 * self._restricted(perspec)
        score += 80 * self._threat_safe_pawns(sqset, perspec)

        for pawn in self.pieces[perspec][chess.PAWN]:
            sqset = chess.SquareSet([pawn])
            score += 24 * self._pawn_push_threat(sqset, perspec, self.pieces[not perspec]['pieces'])

        if self.verbose:
            print(f'Score from threats mid game pieces ({perspec}): {score}')

        return score

## pieces
    def _pieces_mg(self) -> float:
        white_score = self._pieces_mg_color(chess.WHITE)
        black_score = self._pieces_mg_color(chess.BLACK)
        return white_score - black_score

    def _pieces_mg_color(self, perspec = Color):
        score = 0
        score += self._minors_behind_pawn(perspec)
        score += 6 * self._rook_on_queen_file(perspec)
        score += 8 * self._rook_on_king_ring(perspec)
        score += 12 * self._bishop_on_king_ring(perspec)

        # no bonus, semi-open file, open file
        open_file_rook_bonuses = [0, 10, 24]
        for rook in self.pieces[perspec][chess.ROOK]:
            score += open_file_rook_bonuses[self._rook_on_open_or_semi_open_file(rook, perspec)]


        for bishop in self.pieces[perspec][chess.BISHOP]:
            score -= 2 * self._bishop_pawns(bishop, perspec)
            score -= 3 * self._bishop_xray_pawns(bishop, perspec) 
        if self.verbose:
            print(f'Score from Pieces: {perspec}: {score}')
        return score

### Logic

## Pawns
    def _doubled_isolated(self, sq: chess.Square, sq_sqset: SquareSet, color: Color) -> bool:
        return self._isolated(sq, color) and self._doubled(sq_sqset, color)

    def _weak_and_unopposed(self, sq: chess.Square, sq_sqset: SquareSet, color: Color) -> bool:
        if self._opposed(sq_sqset, color):
            return False

        # is it weak?
        # TODO: Backward?
        # return _isolated(sq, my_pawns) or _backward()
        return self._isolated(sq, color)

    # no pawns on adjacent files     
    def _isolated(self, sq: chess.Square, color: Color) -> bool:
        mask = chess.SquareSet(chess.BB_FILES[chess.square_file(sq)])

        left = chess.shift_left(mask)
        right = chess.shift_right(mask)

        adj_file_pawns = (left | right) & self.pieces[color][chess.PAWN]
        return len(adj_file_pawns) == 0

    # In chess, an doubled pawn is a pawn which has another friendly pawn on same file but in Stockfish we attach doubled pawn penalty only for pawn which has another friendly pawn on square directly behind that pawn and is not supported.
    # From https://hxim.github.io/Stockfish-Evaluation-Guide/
    def _doubled(self, sq_sqset: SquareSet, color: Color) -> bool:

        my_pawns = self.pieces[color][chess.PAWN]

        # check if any pawns directly behind
        if color: # white
            mask = chess.shift_down(sq_sqset)
        else:
            mask = chess.shift_up(sq_sqset)

        pawns_right_behind = mask & my_pawns

        if len(pawns_right_behind) == 0:
                return False

        # check if those pawns are supported
        if color: # white, check down, left/right
            mask = chess.shift_down_left(sq_sqset) | chess.shift_down_right(sq_sqset)
        else: # black, check up,left/right
            mask = chess.shift_up_left(sq_sqset) | chess.shift_up_right(sq_sqset)

        support_pawns = mask & my_pawns

        if len(support_pawns) == 0:
                return True

        return False

    # our own pawns are blocked
    def _blocked(self, sq_sqset: SquareSet, color: Color) -> bool:
        if color: # white, blocked are things up
            mask = chess.shift_up(sq_sqset)
        else: # black, blocked are things down
            mask = chess.shift_down(sq_sqset)

        pawns_in_front_of_my_pawns = mask & self.pieces[color][chess.PAWN]

        assert len(pawns_in_front_of_my_pawns) <= 1
        return len(pawns_in_front_of_my_pawns) > 0

    # cannot be safely advanced part needs attacks/moves
    def _backward() -> bool:
        pass


        # def weak_unopposed_pawn():
        #      pass
        # def blocked():
        #      pass

    def _connected_bonus(self, sq: chess.Square, sq_sqset: SquareSet, color: Color) -> int:
            

            supp = self._supported(sq_sqset, color)
            phal = self._phalanx(sq_sqset, color)

            # connected pawns further up are more valuable
            rank_scale = [0, 3, 4, 6, 15, 24, 48]
            if supp or phal: # is connected
                r = self._rank(sq, color)

                if r in (0,7): # first or last rank
                        return 0
                
                opp = self._opposed(sq_sqset, color)
                return rank_scale[r-1] * (2 + int(phal) - int(opp)) + 11 * supp
            else:
                return 0

    # has pawn of opposing color right in front of it
    def _opposed(self, sq_sqset: SquareSet, color: Color) -> bool:
        if color: # white
            mask = chess.shift_up(sq_sqset)
        else:
            mask = chess.shift_down(sq_sqset)

        opposed = mask & self.pieces[not color][chess.PAWN]

        assert len(opposed) <= 1
        return len(opposed) == 1


    def _rank(self, sq: chess.Square, color: Color) -> int:
        if color: # white, so more rank is higher -> if sq is A8, chess.square_rank = 7 and return 7
            return chess.square_rank(sq)
        else: # black, so more rank is lower -> if sq is A3, chess.square_rank = 2 and return 7 - 2 => 5
            return 7 - chess.square_rank(sq)

        # 0 or 1
        # adjacent pawns to phalanx

    def _phalanx(self, sq_sqset: SquareSet, color: Color) -> bool: 
        mask = chess.shift_left(sq_sqset) | chess.shift_right(sq_sqset)
        phalanx_pawns = mask & self.pieces[color][chess.PAWN]
        assert len(phalanx_pawns) <= 2
        return len(phalanx_pawns) >= 1

        # number of pawn defenders: 0,1 or 2

    def _supported(self, sq_sqset: SquareSet, color: Color) -> bool:
            
        if color: # white, check down, left/right
            mask = chess.shift_down_left(sq_sqset) | chess.shift_down_right(sq_sqset)
        else: # black, check up,left/right
            mask = chess.shift_up_left(sq_sqset) | chess.shift_up_right(sq_sqset)
        
        supp_pawns = mask & self.pieces[color][chess.PAWN]
        assert len(supp_pawns) <= 2
        return len(supp_pawns) >= 1


## threats

    # weak enemy not defended by opponent or non pawn weak enemies attacked twice
    # not strongly protected, we just need 
    def _hanging(self, enemy: SquareSet, sq: chess.Square, color: Color) -> bool:

        enemy_pawns = self.pieces[not color][chess.PAWN]

        # not strongly protected
        if sq not in self.weak_enemies[color]:
            return False

        # if enemy is pawn
        enemy_is_pawn = len(enemy & enemy_pawns) == 1

        # if not pawn, 
        if not enemy_is_pawn:
            attackers = self.board.attackers(color, sq)
            n_att = len(attackers)
            defenders = len(self.board.attackers(not color, sq))
            if n_att > defenders:
                return True
            
            has_pawn_attacker = len(self.pieces[color][chess.PAWN] & attackers)
            # if self.board.piece_at(sq) == chess.QUEEN:
            # import pdb; pdb.set_trace()
            # if len(enemy & self.pieces[color][chess.QUEEN]) > 0:
            #     import pdb; pdb.set_trace()
            if has_pawn_attacker:
                return True
            
            # defended more than attacked
            return False
        
        # if it is, but undefended, still hanging
        # defenders are attackers of the opposing color on the square of the enemy (opposing color)
        defenders = len(self.board.attackers(not color, sq))
        return defenders == 0

    
    # if square is weak and our king is attacking that square, we have a king threat
    def _king_threats(self, enemy: SquareSet, sq: chess.Square, color: Color) -> bool:

        if enemy in self.weak_enemies[color]:                
            attackers = self.board.attackers(color, sq)
            king_attackers = self.pieces[color][chess.KING] & attackers
            assert len(king_attackers) <= 1
            return len(king_attackers) == 1
        
        return False

    # if we can move a pawn and threaten a non-pawn enemy piece
    def _pawn_push_threat(self, pawn: SquareSet, color: Color, enemies: SquareSet):
        # this means move two and threatened is 3, then right/left 1

        if color: # white
            # push
            pushed = chess.shift_up(pawn)
            mask = chess.shift_up_left(pushed) | chess.shift_up_right(pushed)
        else:
            pushed = chess.shift_down(pawn)
            mask = chess.shift_down_left(pushed) | chess.shift_down_right(pushed)

        # check if enemy has pieces there
        enemies_attacked = len(mask & enemies)
        assert enemies_attacked <= 2
        if enemies_attacked == 0:
            return 0
        
        # enemy piece there, check if pushed square is safe
        square_and_attacked_by_enemy = pushed & self.attackedBy[not color]['all']

        assert len(square_and_attacked_by_enemy) <= 1
        if len(square_and_attacked_by_enemy) == 1: # not safe
            return 0
        else:
            # safe, return num enemies
            return enemies_attacked
    
    def _threat_safe_pawns(self, enemies: SquareSet, color: Color) -> int:
        # // Protected or unattacked squares
        import pdb; pdb.set_trace()
        safe = ~self.attackedBy[not color]['all'] | self.attackedBy[color]['all']
        safe_pawns = self.pieces[color][chess.PAWN] & safe
        return len(safe_pawns & enemies)


    # bonus for restricting their movement
    def _restricted(self, color):
        # strongly_protected = self.attackedBy[not color][chess.PAWN] | (self.attackedBy2[not color]['all'] & ~self.attackedBy2[color]['all'])
        
        # if defended but not strongly protected and is attacked by us
        mask = self.attackedBy[not color]['all'] & ~self.strongly_protected[not color] & self.attackedBy[color]['all']

        return len(mask)
    
    # Additional bonus if weak piece is only protected by a queen
    # weak = enemy pieces not strongly protected and attacked by us
    def _weak_queen_protection(self, enemy: SquareSet, color: Color):

        return len(self.weak_enemies[color] & self.attackedBy[not color][chess.QUEEN])

    ## TODO
    # def _slider_on_queen(self):
    
    # def _knight_on_queen(self):
    def _get_rook_xray_mask(self, rook: int) -> SquareSet:
        file = chess.square_file(rook)
        rank = chess.square_rank(rook)

        file_mask = SquareSet(chess.BB_FILES[file])
        rank_mask = SquareSet(chess.BB_RANKS[rank])
        return file_mask | rank_mask
    
    def _rook_xray(self, enemy: SquareSet, color: Color) -> bool:
        for rook in self.pieces[color][chess.ROOK]:
            # get file idx

            if len(enemy & self._get_rook_xray_mask(rook)) > 0:
                return True
        return False
    
    def _get_bishop_xray_mask(self, bishop: int):
        file = chess.square_file(bishop)
        rank = chess.square_rank(bishop)

        x = file
        y = rank

        # . . . . . . 1 .
        # . . . . . 1 . .
        # 1 . . . 1 . . .
        # . 1 . 1 . . . .
        # . . . . . . . . <- x,y = (2,3) indexed @ 0
        # . 1 . 1 . . . .
        # 1 . . . 1 . . .
        # . . . . . 1 . .

        to_right = 7 - x # 5
        to_top = 7 - y # 4
        corner=False
        # bot left - one is 0, other is the difference
        ray_1_ax = 0
        ray_1_ay = 0 
        if x < y:
            ray_1_ay = y - x # y=1
        else:
            ray_1_ax = x - y
        
        # top right
        ray_1_bx = 7
        ray_1_by = 7

        if to_right < to_top:
            ray_1_by -= (to_top-to_right)  
        else:
            ray_1_bx -= to_right-to_top #x=6
        
        # corner case top left where both ray endpoitns are becoming the top left
        # just swap to fix (hacky)
        # if both become bottom, corner case for bishop in bot right corner
        # swap
        if ray_1_ax == ray_1_bx and ray_1_ay == ray_1_by:
            corner = True
            ray_1_ax, ray_1_ay = ray_1_ay, ray_1_ax
        
        # from (0,1) to (6,7)
        mask_1 = SquareSet.ray(chess.square(ray_1_ax, ray_1_ay), chess.square(ray_1_bx, ray_1_by))
        # import pdb; pdb.set_trace()
        try:
            assert len(mask_1) <= 8 and len(mask_1) > 0
        except:
            import pdb; pdb.set_trace()

        # top left
        ray_2_ax = 0 
        ray_2_ay = 7
        if x < to_top:
            ray_2_ay = x+y
        else:
            ray_2_ax = x-to_top
        
        # bot right

        ray_2_bx = 7
        ray_2_by = 7
        if y < to_right:
            ray_2_bx -= (to_right-y)
            ray_2_by = 0
        else:
            ray_2_by = y-(to_right)
            ray_2_bx = 7

        # corner case bot left where both ray endpoitns are becoming the bot left

        if ray_2_ax == ray_2_bx == 0 and ray_2_ay == ray_2_by == 0:
            corner = True
            ray_2_ax, ray_2_ay = 7,7
        
        # just swap to fix (hacky)
        # top right for when bishop in top right, swap
        if ray_2_ax == ray_2_bx == 7 and ray_2_ay == ray_2_by == 7:
            corner = True
            ray_2_ax, ray_2_ay = 0,0

        # from (0,1) to (6,7)
        mask_2 = SquareSet.ray(chess.square(ray_2_ax, ray_2_ay), chess.square(ray_2_bx, ray_2_by))
        try:
            assert len(mask_2) <= 8 and len(mask_2) > 0
        except:
            import pdb; pdb.set_trace()

        mask = mask_1 | mask_2
        # if corner:
        #     print(mask)
        return mask

    def _bishop_xray(self, enemy: SquareSet, color: Color) -> bool:
        for bishop in self.pieces[color][chess.BISHOP]:
            mask = self._get_bishop_xray_mask(bishop)
            if len(enemy & mask) > 0:
                return True
        return False

    def _rooks_threat(self, enemy: SquareSet, enemy_sq: chess.Square, color: Color) -> int:
        if len(enemy & self.attackedBy[color][chess.ROOK]) > 0:
            return self.board.piece_type_at(enemy_sq) # 1-6
        elif self._rook_xray(enemy, color):
            return self.board.piece_type_at(enemy_sq)
        return 0

    def _minor_threat(self, enemy: SquareSet, enemy_sq: chess.Square, color: Color) -> int:
        if len(enemy & (self.attackedBy[color][chess.KNIGHT] | self.attackedBy[color][chess.BISHOP])) > 0:
            return self.board.piece_type_at(enemy_sq) # 1-6
        elif self._bishop_xray(enemy, color):
            return self.board.piece_type_at(enemy_sq) # 1-6
        return 0


## pieces

    def _minors_behind_pawn(self, color: Color) -> int:
        minors = self.pieces[color][chess.BISHOP] | self.pieces[color][chess.KNIGHT]
        pawns = self.pieces[color][chess.PAWN]
        if color: 
            minors = chess.shift_up(minors)
        else:
            minors = chess.shift_down(minors)
        return len(pawns & minors)
    
    def _outpost_total(self) -> int:
        pass

    # Number of pawns on the same color square as the bishop multiplied by one plus the number of our blocked pawns in the center files C, D, E or F.
    # penalty for having bishop pawns

    ## // Penalty according to the number of our pawns on the same color square as the
    # // bishop, bigger when the center files are blocked with pawns and smaller
    # // when the bishop is outside the pawn chain.
    def _bishop_pawns(self, bishop: int, color: Color) -> int:
        pawns = self.pieces[color][chess.PAWN]
        light = SquareSet(chess.BB_LIGHT_SQUARES)
        dark = SquareSet(chess.BB_DARK_SQUARES)
        if bishop in light:
            bishop_pawns = light & pawns
        elif bishop in dark:
            bishop_pawns = dark & pawns
        else:
            print('where is the bishop?')
        
        n_bishop_pawns = len(bishop_pawns)
        
        center_pawns = pawns & (chess.BB_FILE_C | chess.BB_FILE_D | chess.BB_FILE_E | chess.BB_FILE_F)

        # blocked if enemy piece on top of advanced pawns
        if color:
            center_pawns = chess.shift_up(center_pawns)
        else:
            center_pawns = chess.shift_down(center_pawns)

        blocked = len(center_pawns & self.pieces[not color]['all'])

        outside_chain = bishop not in self.attackedBy[color][chess.PAWN]
        # more penalty when in the pain chain
        return n_bishop_pawns * (blocked+(0 if outside_chain else 1))

    # Penalty for all enemy pawns xrayed by our bishop.
    def _bishop_xray_pawns(self, bishop: int, color: Color) -> int:
        xray_mask = self._get_bishop_xray_mask(bishop)
        return len(self.pieces[not color][chess.PAWN] & xray_mask)

    # simple bonus for a rook that is on the same file as any queen.
    def _rook_on_queen_file(self, color: Color) -> bool:
        queens = self.pieces[color][chess.QUEEN]
        files = SquareSet()
        for queen in queens:
            files |= chess.BB_FILES[chess.square_file(queen)]

        return len(files & self.pieces[color][chess.ROOK]) > 0
        
    
    def _rook_on_king_ring(self, color: Color) -> bool:
        return self._rook_xray(self.kingRing[not color], color)

    def _bishop_on_king_ring(self, color: Color) -> bool:
        return self._bishop_xray(self.kingRing[not color], color)

    def _rook_on_open_or_semi_open_file(self, rook: int, color: Color) -> int:
        file_bb = SquareSet(chess.BB_FILES[chess.square_file(rook)])

        same_file_pawns = file_bb & self.pieces[color][chess.PAWN]
        # import pdb; pdb.set_trace()
        # print('same file pawns')
        # print(same_file_pawns)
        # print(f'file {chess.square_file(rook)}--\n')
        # print(file_bb)
        if len(same_file_pawns) != 0:
            return 0
        
        same_file_enemy_pawns = file_bb & self.pieces[not color][chess.PAWN]
        is_semi_open = len(same_file_enemy_pawns) > 0
        if is_semi_open:
            return 1
        
        return 2
    
    # piece is n, b, r, q
    def _mobility(self, ):


    # def _trapped_rook(self, rook) -> bool:
    #     if self._rook_on_open_or_semi_open_file(rook):
    #         return False
        
    #     if self._mobility() > 3:
    #         return False
        

        pass

    def _weak_queen(self) -> int:
        pass

    def _queen_infiltration(self) -> int:
        pass

    def _long_diagonal_bishop(self) -> bool:
        pass

    def _king_protector(self) -> bool:
        pass
