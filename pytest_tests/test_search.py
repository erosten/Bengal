from tqdm import tqdm

from .. import Board, Move
from .. import Searcher as PVSearcher


def test_mate_in_threes(m8in3_fens):
    mates = 0
    for fen in tqdm(m8in3_fens):
        board = Board(fen)
        s = PVSearcher()
        score, moves = s.find_move(board, depth=5)
        for m in moves:
            board.push(Move.from_uci(m))

        if board.is_checkmate():
            mates += 1

    assert len(m8in3_fens) - m8in3_fens < 40


def test_mate_in_twos(m8in2_fens):

    for fen in tqdm(m8in2_fens):
        board = Board(fen)
        s = PVSearcher()
        score, moves = s.find_move(board, depth=3)
        for m in moves:
            board.push(Move.from_uci(m))
        assert board.is_checkmate(), 'Didn\'t find mate in 2 for fen {fen}'
