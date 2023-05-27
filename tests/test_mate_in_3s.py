from tqdm import tqdm
import os, sys
thisdir= os.path.dirname(os.path.abspath(__file__))
p_to_src = os.path.abspath(os.path.dirname(thisdir))
sys.path.append(p_to_src)
from src.searcher_ab_ids_hsh_q import Searcher as ABTTQSearcher
from src.searcher_alphabeta import Searcher as ABSearcher
from src.board import Board, Move


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
    # 176 problem for null pruning
    # 205 (?) problem for aspiration windows
    # 235 - PV should be updated on hash moves
    #  
    valid_fens = ['1r4r1/5Q2/3q4/3pk3/4p1p1/6P1/PP4BP/4RR1K w - - 1 0', '2b3rk/1q3p1p/p1p1pPpQ/4N3/2pP4/2P1p1P1/1P4PK/5R2 w - - 1 0', 'rk1q3r/pp1Qbp1p/4pp2/8/4N3/6P1/PP3PBP/2R3K1 w - - 1 0', '5kqQ/1b1r2p1/ppn1p1Bp/2b5/2P2rP1/P4N2/1B5P/4RR1K w - - 1 0', 'qn1r1k2/2r1b1np/pp1pQ1p1/3P2P1/1PP2P2/7R/PB4BP/4R1K1 w - - 1 0', '2b2rk1/2q2pp1/1p1R3p/8/1PBQ4/7P/5PP1/6K1 w - - 1 0', '4r1k1/pR3pp1/1n3P1p/q2p4/5N1P/P1rQpP2/8/2B2RK1 w - - 1 0', '2r3k1/1p1r1p1p/pnb1pB2/5p2/1bP5/1P2QP2/P1B3PP/4RK2 w - - 1 0', '3Q3R/4rqp1/6k1/p3Pp1p/Pp3P1P/1Pp4K/2P5/8 w - - 1 0', 'r1bq1rk1/p3b1np/1pp2ppQ/3nB3/3P4/2NB1N1P/PP3PP1/3R1RK1 w - - 1 0', '2bkr3/5Q1R/p2pp1N1/1p6/8/2q3P1/P4P1K/8 w - - 1 0', '3q2rn/pp3rBk/1npp1p2/5P2/2PPP1RP/2P2B2/P5Q1/6RK w - - 1 0', 'k1br4/ppQ5/8/2PB3p/7b/8/PP6/7K w - - 1 0', 'rr6/p1n4k/1p1NqBp1/2p1P2p/4P3/6R1/bP1Q2PP/4R1K1 w - - 1 0', '3r2qk/p2Q3p/1p3R2/2pPp3/1nb5/6N1/PB4PP/1B4K1 w - - 1 0', '5bk1/1Q3p2/1Np4p/6p1/8/1P2P1PK/4q2P/8 b - - 0 1', 'r4r2/p1p4p/1p2R3/5p2/2B2K2/7k/PPP2P2/8 w - - 1 0', 'kr6/pR5R/1q1pp3/8/1Q6/2P5/PKP5/5r2 w - - 1 0', '6r1/pp3N1k/1q2bQpp/3pP3/8/6RP/PP3PP1/6K1 w - - 1 0', 'r4rk1/p4ppp/Pp4n1/4BN2/1bq5/7Q/2P2PPP/3RR1K1 w - - 1 0', '5q2/1ppr1br1/1p1p1knR/1N4R1/P1P1PP2/1P6/2P4Q/2K5 w - - 1 0', '3r2k1/5p2/2b2Bp1/7p/4p3/5PP1/P3Bq1P/Q3R2K b - - 0 1', 'rq2r2k/pp2p2p/3p1pp1/6R1/4P3/4B3/PPP1Q3/2K4R w - - 1 0', 'r1bq2rk/pp1n1p1p/5P1Q/1B3p2/3B3b/P5R1/2P3PP/3K3R w - - 1 0', 'r1q2b2/p4p1k/1p1r3p/3B1P2/3B2Q1/4P3/P5PP/5RK1 w - - 1 0', '1qr1k3/pb2p3/1p2N3/1NpPp3/8/7Q/PPP5/2K1R3 w - - 1 0', '1k5r/3R1pbp/1B2p3/2NpPn2/5p2/8/1PP3PP/6K1 w - - 1 0', 'r3Rnkr/1b5p/p3NpB1/3p4/1p6/8/PPP3P1/2K2R2 w - - 1 0', '2rq1r1k/1b2bp1p/p1nppp1Q/1p3P2/4P1PP/2N2N2/PPP5/1K1R1B1R w - - 1 0', '5rn1/1q1r3k/7p/3N1p2/P1p1pP2/2Q5/1P4RP/6RK w - - 1 0', '8/6bk/1p6/5pBp/1P2b3/6QP/P5PK/5q2 b - - 0 1', '1k1r4/1p5p/1P3pp1/b7/P3K3/1B3rP1/2N1bP1P/RR6 b - - 0 1', 'r2Q1q1k/pp5r/4B1p1/5p2/P7/4P2R/7P/1R4K1 w - - 1 0', '2q1rb1k/prp3pp/1pn1p3/5p1N/2PP3Q/6R1/PP3PPP/R5K1 w - - 1 0', 'q1r2b1k/rb4np/1p2p2N/pB1n4/6Q1/1P2P3/PB3PPP/2RR2K1 w - - 1 0', '7k/1b1n1q1p/1p1p4/pP2pP1N/P6b/3pB2P/8/1R1Q2K1 b - - 0 1', 'r4rk1/pp4b1/6pp/2pP4/5pKn/P2B2N1/1PQP1Pq1/1RB2R2 b - - 0 1', 'r5k1/p1p3pp/b1p5/3p4/3Nnr2/2P5/PP3qPP/RNQ1R2K b - - 0 1']
    for fen in tqdm(valid_fens):
        if fen_filter != None and fen != fen_filter:
            continue
        board = Board(fen)
        # print(board)
        s = ABTTQSearcher()
        # s = ABSearcher()
        # score, moves = s._search_at_depth(board,depth=4, can_null = False)
        print(fen)
        score, moves = s._search_at_depth(board,depth=5, can_null = True)
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