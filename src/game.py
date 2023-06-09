import chess.pgn

from .agents import Agent, Random, User
from .board import Board
from .hueristic import evaluate
from .utils import display


class Game:
    def __init__(self, agent_w: Agent = Random(), agent_b: Agent = Random(), fen: str = None):
        self.done = False
        self.result = None
        self.agent_w = agent_w
        self.agent_b = agent_b
        if not fen:
            self.board = Board(chess.STARTING_FEN)
        else:
            self.board = Board(fen)

        self.first = self.board.turn
        self.eval_log = []
        display(self.board)

        if isinstance(agent_w, User) and self.board.turn != chess.WHITE:
            raise AttributeError('Fen did not indicate WHITE to move but has been set has the user agent for input')
        elif isinstance(agent_b, User) and self.board.turn != chess.BLACK:
            raise AttributeError('Fen did not indicate BLACK to move but has been set as the user agent for input')

    def eval(self):
        eval = evaluate(self.board)
        self.eval_log.insert(0, eval)
        return eval

    def get_agent_move(self):
        if self.board.turn == chess.WHITE:
            return self.agent_w.get_move(self.board.copy())
        return self.agent_b.get_move(self.board.copy())

    def get_pgn(self):
        return chess.pgn.Game.from_board(self.board)

    def play(self):
        if self.done:
            print('Game is over, start another game.')
            return

        while not self.board.outcome(claim_draw=True):
            turn_color = 'white' if self.board.turn == chess.WHITE else 'black'
            print(f'Current eval ({turn_color}\'s turn): {self.eval()}')

            move = self.get_agent_move()
            if move == 'ff':
                print('You surrendered.')
                break
            self.board.push_uci(move)
            display(self.board)

        self.result = self.board.outcome(claim_draw=True)
        print(f'Game ended with {self.result.result()}, by {self.result.termination}, winner {self.result.winner}')
        self.done = True
        return self.result
