import chess
import random

def get_user_move(board: chess.Board) -> str:
    user_input = input('Make a move: \033[95m')

    print("\033[0m")
    have_valid_move = False if user_input.lower() != 'ff' else True 
    while not have_valid_move:
        try:
            user_move = chess.Move.from_uci(user_input)

            if user_move not in list(board.legal_moves):
                print(f'That move is not legal')
                user_input = input('Please enter a valid move:')
                continue

        except ValueError:
            print(f'Expected a UCI string of length 4 or 5, but got {user_input}')
            user_input = input('Please enter a valid move:')
            continue

        have_valid_move = True
    
    return user_input

def get_random_move(board: chess.Board) -> str:
    legal_moves = list(board.legal_moves)
    return legal_moves[random.randint(0, len(legal_moves)-1)].uci()