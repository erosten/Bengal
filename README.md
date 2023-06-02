# Bengal v0.03

Bengal is a traditional chess engine, written in Python. The goal of this project is to see how far a chess engine written in Python can really go.

With a sophisticated search function, a modified board representation based on the fantastic [python-chess](https://github.com/niklasf/python-chess) and boosted by [PyPy](https://www.pypy.org/), [Bengal is currently around 1900 ELO on lichess](https://lichess.org/@/BengalBot).

# Engine Features

## Search

- Principal Variation Search (Negamax alpha-beta)
- Iterative Deepening
- Opening Books
- Transposition Tables
- Quiescence Search
- Null Move Pruning
- Mate Distance Pruning

## Move Ordering

- Hash (PV) Moves
- Killer Moves
- MVV/LVA
- History Hueristic

## Evaluation

- Material
- Piece Square Tables
- Pawn Structure

# Running Bengal

Bengal is tested on python 3.9, and it's easiest to install dependencies using [conda](https://docs.conda.io/en/latest/miniconda.html#linux-installers)

```
conda create -c conda-forge -n pypy39 pypy python=3.9
```

Installing requirements

```
pip install -r requirements.txt
```

# Changes

See [CHANGELOG.md](CHANGELOG.md)

# Useful Links

This was my first time delving into building a chess engine. Below is a list of useful links, which were invaluable on the journey.

## General Resources

- https://www.chessprogramming.org/Main_Page
- https://python-chess.readthedocs.io/en/latest/core.html#board

## Python Chess Repositories

- https://github.com/thomasahle/sunfish
- https://github.com/Disservin/python-chess-engine
- https://github.com/Alex2262/Antares
