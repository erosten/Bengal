import time
import pytest
import chess.engine
from pathlib import Path
import tqdm
from ..src.board import Board, WHITE




@pytest.mark.asyncio
async def test_self_play():

    bengal_engine_path = Path(__file__).absolute().parent.parent / 'bengal.sh'
    _transport, engine = await chess.engine.popen_uci(bengal_engine_path)

    wtime = 60 
    btime = 60
    winc = 1
    binc = 1 

    board = Board()
    with tqdm.tqdm(total=100) as pbar:
        while not board.is_game_over():
            limit = chess.engine.Limit(
                white_clock=wtime,
                black_clock=btime,
                white_inc=winc,
                black_inc=binc)
            
            start = time.time()
            result = await engine.play(board, limit)
            elapsed = time.time() - start
            board.push(result.move)

            if board.turn is WHITE:
                wtime -= elapsed - winc
                if wtime < 0:
                    return
            else:
                btime -= elapsed - winc
                if btime < 0:
                    return
            pbar.update(1)
    print(f'Self-play: {board.outcome()}')
    assert board.outcome().result is not None
            
