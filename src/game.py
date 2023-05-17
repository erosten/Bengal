import chess
import chess.pgn
from .agents import Agent, RandomAgent, UserAgent
from .ai.evaluations import get_eval_expl_fn
from .utils import is_draw, display


class Game:
    def __init__(self, agent_w: Agent = RandomAgent(), agent_b: Agent = RandomAgent(), fen: str = None):
        self.done = False
        self.agent_w = agent_w
        self.agent_b = agent_b
        if not fen:
            self.board = chess.Board(chess.STARTING_FEN)
        else:
            self.board = chess.Board(fen)
        
        self.first = self.board.turn
        self.eval_log = []
        display(self.board)

        self.eval_fn = get_eval_expl_fn('dynamic_tricks')

        if isinstance(agent_w, UserAgent) and self.board.turn != chess.WHITE:
            raise AttributeError('Fen did not indicate WHITE to move but has been set has the user agent for input')
        elif isinstance(agent_b, UserAgent) and self.board.turn != chess.BLACK:
            raise AttributeError('Fen did not indicate BLACK to move but has been set as the user agent for input')
        

    def eval(self):
        eval = self.eval_fn(self.board)
        self.eval_log.insert(0, eval)
        return eval
    
    def get_agent_move(self):
        if self.board.turn == chess.WHITE:
            return self.agent_w.get_move(self.board.copy())
        return self.agent_b.get_move(self.board.copy())

    def get_pgn(self):
        return chess.pgn.Game.from_board(self.board)
    
    def save_evals(self):
        import matplotlib.pyplot as plt
        plys = [x for x in range(len(self.eval_log))]

        plt.plot(plys, self.eval_log)
        plt.xlabel('Ply')
        plt.ylabel('Eval Favoring White')
        
    
    def play(self):
        if self.done:
            print('Game is over, start another game.')
            return
        
        while not self.board.is_checkmate() or is_draw(self.board):
            turn_color = 'white' if self.board.turn == chess.WHITE else 'black'
            print(f'Current eval ({turn_color}\'s turn): {self.eval()}')

            move = self.get_agent_move()
            if move == 'ff':
                print('You surrendered.')
                break
            self.board.push_uci(move)
            display(self.board)
        
        self.done = True

        