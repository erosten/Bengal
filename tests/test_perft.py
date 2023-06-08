from chess import Board as ChessBoard
from chess import BoardT as ChessBoardT
from .. import Board as CustomBoard
from .. import BoardT as CustomBoardT

from tqdm import tqdm



def perft_test(depth: int, board: CustomBoardT) -> int:
    if depth >= 1:
        count = 0
        move_gen = board.get_legal_generator(board.generate_sorted_pseudo_legal_moves())
        for move, move_type in move_gen:
            board.push(move)
            count += perft_test(depth - 1, board)
            board.pop()

        return count
    else:
        return 1


def perft(depth: int, board: ChessBoardT) -> int:
    if depth >= 1:
        count = 0

        for move in board.generate_legal_moves():
            board.push(move)
            count += perft(depth - 1, board)
            board.pop()

        return count
    else:
        return 1



def test_perft(m8in3_fens, m8in2_fens, perft_fen_data):

    for fen in tqdm(m8in3_fens, desc = 'Mate in 3 perft'):
        actual = perft(3, ChessBoard(fen))
        pred = perft_test(3, CustomBoard(fen))
        assert actual == pred
    
    for fen in tqdm(m8in2_fens, desc = 'Mate in 2 perft'):
        actual = perft(3, ChessBoard(fen))
        pred = perft_test(3, CustomBoard(fen))
        assert actual == pred
    
    d = sorted(perft_fen_data, key=lambda x: x['depth'])
    for test in tqdm(d, desc = 'Various Position perft'):
        depth = test['depth']
        fen = test['fen']
        actual = perft(depth, ChessBoard(fen))
        pred = perft_test(depth, CustomBoard(fen))
        assert actual == pred    

