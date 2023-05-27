def display(board):

        # def print_board(self, board_state, captured={"w": [], "b": []}):

    print('\n------------------------------------------------------------------\n')
    PIECE_SYMBOLS = {'P': '♟',
                    'B': '♝',
                    'N': '♞',
                    'R': '♜',
                    'Q': '♛',
                    'K': '♚',
                    'p': '\033[36m\033[1m♙\033[0m',
                    'b': '\033[36m\033[1m♗\033[0m',
                    'n': '\033[36m\033[1m♘\033[0m',
                    'r': '\033[36m\033[1m♖\033[0m',
                    'q': '\033[36m\033[1m♕\033[0m',
                    'k': '\033[36m\033[1m♔\033[0m'}

    board_state = board.fen()

    board_state = board_state.split()[0].split("/")
    board_state_str = "\n"
    white_captured = " ".join(PIECE_SYMBOLS[piece] for piece in [])
    black_captured = " ".join(PIECE_SYMBOLS[piece] for piece in [])
    # import pdb; pdb.set_trace()
    for i, row in enumerate(board_state):
        board_state_str += str(8-i)
        for char in row:
            if char.isdigit():
                board_state_str += " ♢" * int(char)
            else:
                board_state_str += " " + PIECE_SYMBOLS[char]
        if i == 0:
            board_state_str += "   Captured:" if len(white_captured) > 0 else ""
        if i == 1:
            board_state_str += "   " + white_captured
        if i == 6:
            board_state_str += "   Captured:" if len(black_captured) > 0 else ""
        if i == 7:
            board_state_str += "   " + black_captured
        board_state_str += "\n"
    board_state_str += "  A B C D E F G H"
    print(board_state_str)
    print('\n------------------------------------------------------------------\n')
