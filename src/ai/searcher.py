


class Searcher:
    def __init__(self):



        pass


    def negamax(self, position, gamma, depth, root=True):







    def search(self, board):

        max_ = -987654
        best_moves = []
        for move in list(board.legal_moves):
            board.push(move)

            # negamax
