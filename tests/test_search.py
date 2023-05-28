import json
import os
import sys
from pathlib import Path

thisdir = os.path.dirname(os.path.abspath(__file__))
p_to_src = os.path.abspath(os.path.dirname(thisdir))
sys.path.append(p_to_src)
import cProfile
import pstats
import time

import tabulate
from tqdm import tqdm

from src.board import Board
from src.searcher_ab_ids_hsh_q import Searcher as ABTTQSearcher
from src.searcher_alphabeta import Searcher as ABSearcher
from src.searcher_negamax import Searcher
from src.searcher_pvs import Searcher as PVSearcher
from src.utils import display


def load_data():
    with open(os.path.join(thisdir, './data/search_test_data.json'), 'r') as f:
        return json.load(f)


profiler = cProfile.Profile()


def test(filter=None):
    d = load_data()
    results = []

    for test in tqdm(d):
        n = test['nodes']
        d = test['depth']
        fen = test['fen']
        if filter and fen != filter:
            continue

        b = Board(fen)
        s = Searcher()
        # s = PVSearcher()
        # s = ABSearcher()
        s = ABTTQSearcher()
        s = PVSearcher()
        t1 = time.time()
        profiler.enable()
        # score,m = s._search_at_depth(b,depth=d)
        score, pv = s.find_move(b, depth=d)
        profiler.disable()
        t = time.time() - t1
        results.append((test, (t, pv[0], s.nodes, score)))
    return results


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', type=str, default='')
    parser.add_argument('--filter', default=None)
    args = parser.parse_args()
    out_f = args.o
    filter = args.filter
    res = test(filter)

    # dump stats
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    import datetime

    dt = datetime.datetime.now()
    out_p = Path('./stats_search')

    if not out_p.exists():
        out_p.mkdir(exist_ok=True, parents=True)

    if out_f != '':
        out_p = out_p / out_f
    else:
        out_p = out_p / f"run_{dt.strftime('%Y_%m_%d')}.prof"

    stats.dump_stats(str(out_p))
    print(f'Stats dumped to {out_f}')

    data = [
        (
            f"{t['depth']} {Board(t['fen']).turn}",
            t['nodes'],
            ts_n,  # Nodes
            t['perft_time'],
            t['mini_time'],
            ts_t,  # Time
            t['mini_move'],
            ts_m,
            t['best_move'],  # Moves
            t['mini_score'],
            ts_s,  # Scores
            t['comments'],  # Comments
        )
        for t, (ts_t, ts_m, ts_n, ts_s) in res
    ]
    data.sort(key=lambda x: x[1], reverse=True)  # sort by nodes, most at top
    headers = [
        'Depth',
        'Nodes',
        'TS Nodes*',
        'perft (s)',
        'mini (s)',
        'TS (s)*',
        'mini (mv)',
        'TS* (mv)',
        'best',
        'mini',
        'TS*',
        '',
    ]

    table = tabulate.tabulate(data, headers=headers, tablefmt='grid')

    print(table)
