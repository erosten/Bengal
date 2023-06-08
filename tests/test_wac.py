from tqdm import tqdm

from .. import Board, Move
from .. import Searcher as PVSearcher

# https://www.talkchess.com/forum3/viewtopic.php?f=2&t=67469
def test_wac200(wac200):
    # warmup pypy
    s = PVSearcher()
    s.find_move(Board(), depth = 7)
    print('Warmup done')
    points, total = 0,0
    for epd in tqdm(wac200):
        board, opts = Board.from_epd(epd)
        s = PVSearcher()
        _, moves = s.find_move(board, max_time = 2, strict_time=True)
        if "bm" in opts:
            total += 1
            if Move.from_uci(moves[0]) in opts["bm"]:
                points += 1
    
    print(f'Points: {points}/{total}')
    assert points / total > 0.5