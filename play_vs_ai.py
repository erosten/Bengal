from game import Game
from agents import NegaMax, AlphaBetaTTQ, User

def run_game(fen: str):
    agent_b = AlphaBetaTTQ(depth=5)
    agent_w = User()
    game = Game(agent_w, agent_b, fen)
    game.play()

    pgn = game.get_pgn()
    print(pgn)
    
if __name__ == '__main__':
    # Italian Game
    # fen = 'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3'
    # mate in 2
    fen = 'r1b2k1r/ppp1bppp/8/1B1Q4/5q2/2P5/PPP2PPP/R3R1K1 w - - 1 0'
    # reg
    # fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    # isolated pawns
    #1
    # fen = '4k3/ppp2ppp/8/8/4P3/8/PPP3PP/4K3 w - - 0 1'
    #2
    # fen = '3r1k2/2p2pbp/1p2p3/p5P1/3PBP2/6P1/6K1/7R w - - 0 1'

    # hanging queen - black to move
    fen = 'rn1qkbnr/ppp1pppp/8/3p1b2/3P4/P2Q4/1PP1PPPP/RNB1KBNR b KQkq - 0 3'
    run_game(fen)
