import chess
import chess.pgn
from .agents import Agent, UserAgent
from .ai.evaluations import get_eval_expl_fn
from .utils import is_draw, display


class Game:
    def __init__(self, agent_w: Agent = UserAgent(), agent_b: Agent = UserAgent(), fen: str = None):
        self.done = False
        self.agent_w = agent_w
        self.agent_b = agent_b
        if not fen:
            self.board = chess.Board(chess.STARTING_FEN)
        else:
            self.board = chess.Board(fen)
        display(self.board)

        self.eval_fn = get_eval_expl_fn('dynamic_pst')
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
        
        while not self.board.is_checkmate() or is_draw(self.board):
            turn_color = 'white' if self.board.turn == chess.WHITE else 'black'
            print(f'Current eval ({turn_color}\'s turn): {self.eval_fn(self.board)}')

            move = self.get_agent_move()
            if move == 'ff':
                print('You surrendered.')
                break
            self.board.push_uci(move)
            display(self.board)
        
        self.done = True

        