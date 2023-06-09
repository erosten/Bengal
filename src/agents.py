import random
from abc import ABC, abstractmethod

from .board import BoardT, Move
from .searcher_pvs import Searcher as PVSearcher


class Agent(ABC):
    @abstractmethod
    def get_move(self) -> str:
        pass


def get_user_move(board: BoardT) -> str:
    user_input = input('Make a move: \033[95m')

    print("\033[0m")
    have_valid_move = False if user_input.lower() != 'ff' else True
    while not have_valid_move:
        try:
            user_move = Move.from_uci(user_input)

            if user_move not in list(board.legal_moves):
                print('That move is not legal')
                user_input = input('Please enter a valid move:')
                continue

        except ValueError:
            print(f'Expected a UCI string of length 4 or 5, but got {user_input}')
            user_input = input('Please enter a valid move:')
            continue

        have_valid_move = True

    return user_input


def get_random_move(board: BoardT) -> str:
    legal_moves = list(board.legal_moves)
    return legal_moves[random.randint(0, len(legal_moves) - 1)].uci()


class Random:
    def __init__(self, seed: int = 42):
        self.seed = seed

    def get_move(self, board: BoardT) -> str:
        random.seed(self.seed)
        return get_random_move(board)


class User:
    def get_move(self, board: BoardT) -> str:
        return get_user_move(board)


class PrincipalV:
    def __init__(self, depth: int = 3):
        self.depth = depth
        self.searcher = PVSearcher()

    def get_move(self, board: BoardT) -> str:
        score, pv = self.searcher.find_move(board, self.depth)
        return pv[0]
