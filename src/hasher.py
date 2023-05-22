class ZobristHasher:
    def __init__(self, array: List[int]) -> None:
        assert len(array) >= 781
        self.array = array

    def hash_board(self, board: chess.BaseBoard) -> int:
        zobrist_hash = 0

        for pivot, squares in enumerate(board.occupied_co):
            for square in chess.scan_reversed(squares):
                piece_index = (typing.cast(chess.PieceType, board.piece_type_at(square)) - 1) * 2 + pivot
                zobrist_hash ^= self.array[64 * piece_index + square]

        return zobrist_hash

    def hash_castling(self, board: chess.Board) -> int:
        zobrist_hash = 0

        # Hash in the castling flags.
        if board.has_kingside_castling_rights(chess.WHITE):
            zobrist_hash ^= self.array[768]
        if board.has_queenside_castling_rights(chess.WHITE):
            zobrist_hash ^= self.array[768 + 1]
        if board.has_kingside_castling_rights(chess.BLACK):
            zobrist_hash ^= self.array[768 + 2]
        if board.has_queenside_castling_rights(chess.BLACK):
            zobrist_hash ^= self.array[768 + 3]

        return zobrist_hash

    def hash_ep_square(self, board: chess.Board) -> int:
        # Hash in the en passant file.
        if board.ep_square:
            # But only if there's actually a pawn ready to capture it. Legality
            # of the potential capture is irrelevant.
            if board.turn == chess.WHITE:
                ep_mask = chess.shift_down(chess.BB_SQUARES[board.ep_square])
            else:
                ep_mask = chess.shift_up(chess.BB_SQUARES[board.ep_square])
            ep_mask = chess.shift_left(ep_mask) | chess.shift_right(ep_mask)

            if ep_mask & board.pawns & board.occupied_co[board.turn]:
                return self.array[772 + chess.square_file(board.ep_square)]
        return 0

    def hash_turn(self, board: chess.Board) -> int:
        # Hash in the turn.
        return self.array[780] if board.turn == chess.WHITE else 0

    def __call__(self, board: chess.Board) -> int:
        return (self.hash_board(board) ^ self.hash_castling(board) ^
                self.hash_ep_square(board) ^ self.hash_turn(board))