import sys
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from src.board import STARTING_BOARD_FEN, Board, BoardT
from src.searcher_pvs import Searcher
from src.utils import logger, set_logger_level


set_logger_level('ERROR')

DEFAULT_MAX_DEPTH = 100


def go_loop(
    searcher: Searcher,
    board: BoardT,
    stop_event: Event,
    max_movetime: int = 0,
    strict_time: bool = False,
    max_depth: int = 100,
    debug: bool = False,
):

    if debug:
        print(f"Going movetime={max_movetime}, depth={max_depth}", flush=True)

    start = time.time()
    depth = 0
    t1 = start
    t_search = 0
    for score, pv in searcher._search_at_depth(board, max_depth):
        # Time Management
        t2 = time.time()
        t_search += t2 - t1
        depth += 1

        elapsed = time.time() - start
        fields = {
            "depth": depth,
            "time": round(1000 * elapsed),
            "nodes": searcher.nodes,
            "nps": round(searcher.nodes / elapsed),
            "score cp": score,
            "pv": ' '.join(pv),
        }
        info_str = " ".join(f"{k} {v}" for k, v in fields.items())
        print(f"info {info_str}",flush=True)

        # Have a move (depth > 1), break conditions below
        if depth > 1:
            # Depth limiting case
            if depth - 1 >= max_depth:
                break
            # same time for last depth search will put us over 
            # and we are in strict time, just break now
            if strict_time and (elapsed + t_search > max_movetime):
                break
            # currently over time, break now
            if elapsed > max_movetime:
                break
            if stop_event.is_set():
                break

    # FIXME: If we are in "go infinite" we aren't actually supposed to stop the
    # go-loop before we got stop_event. Unfortunately we currently don't know if
    # we are in "go infinite" since it's simply translated to "go depth 100".

    print("bestmove", pv[0] if pv else "(none)",flush=True)


def main():
    """
    Partially implemented UCI protocol
    """
    debug = True
    searcher = Searcher()
    board = Board()
    pos_hist = set()
    N_MOVES = 100
    with ThreadPoolExecutor() as exec:
        # Noop future to get started
        go_future = exec.submit(lambda: None)
        do_stop_event = Event()

        while True:
            try:
                args = input().split()
                if not args:
                    continue

                elif args[0] == 'quit':
                    if go_future.running():
                        do_stop_event.set()
                        go_future.result()
                    break

                elif args[0] == 'stop':
                    if go_future.running():
                        do_stop_event.set()
                        go_future.result()

                elif args[0] == 'uci':
                    print('id name Bengal')
                    print('id author erosten')
                    print('uciok')

                elif args[0] == 'isready':
                    print('readyok')

                elif args[0] == 'debug':
                    if args[1] == 'on':
                        debug = True
                    elif args[1] == 'off':
                        debug = False

                elif args[0] == "position":
                    if args[1] == 'startpos':
                        board = Board(STARTING_BOARD_FEN)
                        pos_hist.clear()
                        pos_hist.add(board._board_pieces_state())
                        N_MOVES = 100

                        for move in args[3:]:
                            board.push_uci(move)
                            pos_hist.add(board._board_pieces_state())
                            N_MOVES -= 1

                    elif args[1] == 'fen':
                        fen = ' '.join(args[2:8])
                        board = Board(fen=fen)
                        pos_hist.clear()
                        pos_hist.add(board._board_pieces_state())
                        N_MOVES = 100

                        if len(args) > 8:
                            for move in args[9:]:
                                board.push_uci(move)
                                pos_hist.add(board._board_pieces_state())
                                N_MOVES -= 1

                    searcher = Searcher(pos_hist=pos_hist)

                elif args[0] == "go":
                    max_depth = 100
                    strict = False
                    ttm = 100000
                    if args[1:] == [] or args[1] == 'infinite':
                        pass
                    elif args[1] == 'movetime':
                        ttm = int(args[2]) / 1000  # seconds
                    elif args[1] == 'wtime':
                        # in seconds
                        wtime, btime = int(args[2]) / 1000, int(args[4]) / 1000
                        if args[5] == 'mvoestogo':
                            movestogo = int(args[6])
                        else:
                            movestogo = N_MOVES
                        t_tot = wtime if board.turn else btime

                        ttm = t_tot / movestogo
                        strict = t_tot < 30

                    elif args[1] == 'depth':
                        max_depth = int(args[2])

                    N_MOVES -= 1
                    do_stop_event.clear()
                    go_future = exec.submit(
                        go_loop, 
                        searcher, 
                        board, 
                        do_stop_event, 
                        ttm, 
                        strict, 
                        max_depth, 
                        debug
                    )

                    # Make sure we get informed if the job fails
                    def callback(fut):
                        fut.result(timeout=0)

                    go_future.add_done_callback(callback)
            except (KeyboardInterrupt, EOFError):
                if go_future.running():
                    if debug:
                        print("Stopping go loop...")
                    do_stop_event.set()
                    go_future.result()
                break


if __name__ == "__main__":
    main()
