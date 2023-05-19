from typing import Optional, Iterator

# objects
from chess import Board, Move, Bitboard

# constants
from chess import STARTING_FEN
from chess import KNIGHT, BISHOP, QUEEN, ROOK
from chess import BB_ALL, BB_RANK_3, BB_RANK_4, BB_RANK_5, BB_RANK_6
from chess import WHITE, BLACK, BB_PAWN_ATTACKS 
# utility fns
from chess import msb, scan_reversed, square_rank

# todo
# implement get move functions
# making checking more efficient
class BoardState(Board):
    def __init__(self, *args, **kwargs):
        super(BoardState, self).__init__(*args, **kwargs)

    def generate_sorted_moves(self, from_mask: Bitboard = BB_ALL, to_mask: Bitboard = BB_ALL) -> Iterator[Move]:
        if self.is_variant_end():
            return

        king_mask = self.kings & self.occupied_co[self.turn]
        if king_mask:
            king = msb(king_mask)
            blockers = self._slider_blockers(king)
            checkers = self.attackers_mask(not self.turn, king)
            if checkers:
                for move in self._generate_evasions(king, checkers, from_mask, to_mask):
                    if self._is_safe(king, blockers, move):
                        yield move
            else:
                for move in self.generate_sorted_pseudo_legal_moves(from_mask, to_mask):
                    if self._is_safe(king, blockers, move):
                        yield move
        else:
            yield from self.generate_sorted_pseudo_legal_moves(from_mask, to_mask)



    # Moves that are OK here
    # Moving king into check
    # Moving a piece that is blocking a checked king
    # En passant that moves out of a pin on king (some other stuff maybe?)
    def generate_sorted_pseudo_legal_moves(self, from_mask: Bitboard = BB_ALL, to_mask: Bitboard = BB_ALL) -> Iterator[Move]:
        our_pieces = self.occupied_co[self.turn]
        enemy_pieces = self.occupied_co[not self.turn]
        

        # pawn captures that are not pawns
        pawns = self.pawns & our_pieces & from_mask
        for from_square in scan_reversed(pawns):
            targets = (
                BB_PAWN_ATTACKS[self.turn][from_square] &
                self.occupied_co[not self.turn] & to_mask)

            for to_square in scan_reversed(targets):
                # en passant captures 
                if square_rank(to_square) in [0, 7]:
                    yield Move(from_square, to_square, QUEEN)
                    yield Move(from_square, to_square, ROOK)
                    yield Move(from_square, to_square, BISHOP)
                    yield Move(from_square, to_square, KNIGHT)
                else:
                    yield Move(from_square, to_square)

        # other captures
        # from most -> least valuable victim
        # so in reverse is least valuable attacker
        pieces = [self.queens, self.rooks, self.bishops, self.knights, self.pawns]
        v_mask = ~our_pieces & to_mask

        for i in range(len(pieces)):
            victims = enemy_pieces & pieces[i]

            if not victims:
                continue

            for j in range(len(pieces)-2, -1, -1):
                attackers = our_pieces & pieces[j]

                # yield moves between victims/attackers
                for a in scan_reversed(attackers):
                    att_vics = self.attacks_mask(a) & ~our_pieces & to_mask & victims 

                    for v in scan_reversed(att_vics):
                            yield Move(a, v) 

        # only attacks remaining are kings
        king_mask = self.kings & our_pieces
        if king_mask:
            king = msb(king_mask)
            moves = self.attacks_mask(king) & enemy_pieces & to_mask
            for to_square in scan_reversed(moves):
                yield Move(king, to_square)
            
        
        # Generate castling moves.
        if from_mask & self.kings:
            yield from self.generate_castling_moves(from_mask, to_mask)

        # non-attacking piece moves
        # attacks mask moves minus opp pieces
        non_pawns = our_pieces & ~self.pawns & from_mask
        for from_sq in scan_reversed(non_pawns):
            moves = self.attacks_mask(from_sq) & ~our_pieces & to_mask & ~enemy_pieces
            for to_sq in scan_reversed(moves):
                yield Move(from_sq, to_sq)

        # rest are non-capture pawn moves
        # Prepare pawn advance generation.
        if self.turn == WHITE:
            single_moves = pawns << 8 & ~self.occupied
            double_moves = single_moves << 8 & ~self.occupied & (BB_RANK_3 | BB_RANK_4)
        else:
            single_moves = pawns >> 8 & ~self.occupied
            double_moves = single_moves >> 8 & ~self.occupied & (BB_RANK_6 | BB_RANK_5)

        single_moves &= to_mask
        double_moves &= to_mask

        # Generate single pawn moves.
        for to_square in scan_reversed(single_moves):
            from_square = to_square + (8 if self.turn == BLACK else -8)

            if square_rank(to_square) in [0, 7]:
                yield Move(from_square, to_square, QUEEN)
                yield Move(from_square, to_square, ROOK)
                yield Move(from_square, to_square, BISHOP)
                yield Move(from_square, to_square, KNIGHT)
            else:
                yield Move(from_square, to_square)

        # Generate double pawn moves.
        for to_square in scan_reversed(double_moves):
            from_square = to_square + (16 if self.turn == BLACK else -16)
            yield Move(from_square, to_square)

        # Generate en passants
        if self.ep_square:
            yield from self.generate_pseudo_legal_ep(from_mask, to_mask)


    # generate_legal_moves from python-chess
    def generate_legal_moves(self, from_mask: Bitboard = BB_ALL, to_mask: Bitboard = BB_ALL) -> Iterator[Move]:
        if self.is_variant_end():
            return

        king_mask = self.kings & self.occupied_co[self.turn]
        if king_mask:
            king = msb(king_mask)
            blockers = self._slider_blockers(king)
            checkers = self.attackers_mask(not self.turn, king)
            if checkers:
                for move in self._generate_evasions(king, checkers, from_mask, to_mask):
                    if self._is_safe(king, blockers, move):
                        yield move
            else:
                for move in self.generate_pseudo_legal_moves(from_mask, to_mask):
                    if self._is_safe(king, blockers, move):
                        yield move
        else:
            yield from self.generate_pseudo_legal_moves(from_mask, to_mask)

    def generate_pseudo_legal_moves(self, from_mask: Bitboard = BB_ALL, to_mask: Bitboard = BB_ALL) -> Iterator[Move]:
        our_pieces = self.occupied_co[self.turn]

        # Generate piece moves.
        non_pawns = our_pieces & ~self.pawns & from_mask
        for from_square in scan_reversed(non_pawns):
            moves = self.attacks_mask(from_square) & ~our_pieces & to_mask
            for to_square in scan_reversed(moves):
                yield Move(from_square, to_square)

        # Generate castling moves.
        if from_mask & self.kings:
            yield from self.generate_castling_moves(from_mask, to_mask)

        # The remaining moves are all pawn moves.
        pawns = self.pawns & self.occupied_co[self.turn] & from_mask
        if not pawns:
            return

        # Generate pawn captures.
        capturers = pawns
        for from_square in scan_reversed(capturers):
            targets = (
                BB_PAWN_ATTACKS[self.turn][from_square] &
                self.occupied_co[not self.turn] & to_mask)

            for to_square in scan_reversed(targets):
                if square_rank(to_square) in [0, 7]:
                    yield Move(from_square, to_square, QUEEN)
                    yield Move(from_square, to_square, ROOK)
                    yield Move(from_square, to_square, BISHOP)
                    yield Move(from_square, to_square, KNIGHT)
                else:
                    yield Move(from_square, to_square)

        # Prepare pawn advance generation.
        if self.turn == WHITE:
            single_moves = pawns << 8 & ~self.occupied
            double_moves = single_moves << 8 & ~self.occupied & (BB_RANK_3 | BB_RANK_4)
        else:
            single_moves = pawns >> 8 & ~self.occupied
            double_moves = single_moves >> 8 & ~self.occupied & (BB_RANK_6 | BB_RANK_5)

        single_moves &= to_mask
        double_moves &= to_mask

        # Generate single pawn moves.
        for to_square in scan_reversed(single_moves):
            from_square = to_square + (8 if self.turn == BLACK else -8)

            if square_rank(to_square) in [0, 7]:
                yield Move(from_square, to_square, QUEEN)
                yield Move(from_square, to_square, ROOK)
                yield Move(from_square, to_square, BISHOP)
                yield Move(from_square, to_square, KNIGHT)
            else:
                yield Move(from_square, to_square)

        # Generate double pawn moves.
        for to_square in scan_reversed(double_moves):
            from_square = to_square + (16 if self.turn == BLACK else -16)
            yield Move(from_square, to_square)

        # Generate en passant captures.
        if self.ep_square:
            yield from self.generate_pseudo_legal_ep(from_mask, to_mask)