from game import Game
from agents import NegaMax, AlphaBetaTTQ, Random


def run_game(fen: str):
    try:
        agent_w = AlphaBetaTTQ(depth=8)
        agent_b = AlphaBetaTTQ(depth=3)
        game = Game(agent_w, agent_b, fen)
        game.play()
    except KeyboardInterrupt:
        pass

    pgn = game.get_pgn()
    print(pgn)
    # print(f'Total time thinking for W: {tot}')
    

if __name__ == '__main__':
    # Italian Game
    fen = 'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3'
    # mate in 2
    # fen = 'r1b2k1r/ppp1bppp/8/1B1Q4/5q2/2P5/PPP2PPP/R3R1K1 w - - 1 0'
    # reg
    # fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    # fen = 'rn1qkbnr/pp2pppp/2p5/3p1b2/3PQ3/P7/1PP1PPPP/RNB1KBNR b KQkq - 1 4'
    # fen = 'r1bqkb1r/pppp1ppp/8/4p3/P1B1n3/2N2Q2/1PPP1PPP/R1B2RK1 b kq - 0 7'
    # fen = 'r1bqk2r/pppp1ppp/2n5/8/1bBPn3/2N2N2/PP3PPP/R1BQ1RK1 b kq - 1 8'
    run_game(fen)