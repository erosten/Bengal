from src.game import Game
from src.agents import NegaMax, AlphaBetaTTQ, Random
def run_game(fen: str):
    try:
        agent_w = Random()
        agent_b = AlphaBetaTTQ(depth=10)
        game = Game(agent_w, agent_b, fen)
        game.play()
    except KeyboardInterrupt:
        pass

    pgn = game.get_pgn()
    print(pgn)
    

if __name__ == '__main__':
    # Italian Game
    fen = 'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3'
    # mate in 2
    # fen = 'r1b2k1r/ppp1bppp/8/1B1Q4/5q2/2P5/PPP2PPP/R3R1K1 w - - 1 0'
    # reg
    # fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    # fen = 'rn1qkbnr/pp2pppp/2p5/3p1b2/3PQ3/P7/1PP1PPPP/RNB1KBNR b KQkq - 1 4'

    run_game(fen)
