from tqdm import tqdm
import os, sys
thisdir= os.path.dirname(os.path.abspath(__file__))
p_to_src = os.path.abspath(os.path.dirname(thisdir))
sys.path.append(p_to_src)
from src.searcher_ab_ids_hsh_q import Searcher as ABTTQSearcher
from src.searcher_alphabeta import Searcher as ABSearcher
from src.chess import Board, Move


def test_mate_in_threes(fen_filter):
    fname = './data/mate_in_3.txt'

    data = open(fname).read().splitlines()
    data = [d for d in data if d!='']
    # s = ABSearcher
    valid_fens = []
    for datum in data:
        try:
            Board(datum)
            valid_fens.append(datum)
        except:
            continue


    invalid_fens = []
    for fen in tqdm(valid_fens[:10]):
        if fen_filter != None and fen != fen_filter:
            continue
        board = Board(fen)
        # print(board)
        s = ABTTQSearcher()
        # s = ABSearcher()
        # score, moves = s._search_at_depth(board,depth=4, can_null = False)
        print(fen)
        score, moves = s._search_at_depth(board,depth=5, can_null = False)
        for m in moves:
            board.push(Move.from_uci(m))
        try:
            assert board.is_checkmate(), board
        except:
            print(f'Didn\'t find mate in 3 for fen {fen}')
            invalid_fens.append(fen)

    print(f'Found {len(valid_fens) - len(invalid_fens)}/{len(valid_fens)} valid, {len(invalid_fens)} invalid')
    import pdb; pdb.set_trace()


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--fen')
    fen = p.parse_args().fen
    test_mate_in_threes(fen)