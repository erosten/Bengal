# Bengal v0.03

Bengal is a traditional chess engine, written in Python. The goal of this project is to see how far a chess engine written in Python can really go.

With a principal variation search function, a modified board representation based on the fantastic [python-chess](https://github.com/niklasf/python-chess) and boosted by [PyPy](https://www.pypy.org/), [Bengal is currently around 1900 ELO on lichess](https://lichess.org/@/BengalBot) and I hope to continue to improve Bengal's strength.

This code is being actively developed. If something does not work or you encounter any problems, please feel free to open an issue and let me know.

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
conda env update -n pypy39 --file environment_pypy.yaml
```

Activate the environment

```
conda activate pypy39
```

The easiest way to play bengal is through the terminal

```
python3 play_vs_ai.py
```

Make a move like `e2e4`

```
------------------------------------------------------------------


8 ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖
7 ♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙   
6 ♢ ♢ ♢ ♢ ♢ ♢ ♢ ♢
5 ♢ ♢ ♢ ♢ ♢ ♢ ♢ ♢
4 ♢ ♢ ♢ ♢ ♢ ♢ ♢ ♢
3 ♢ ♢ ♢ ♢ ♢ ♢ ♢ ♢
2 ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟
1 ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜   
  A B C D E F G H

------------------------------------------------------------------

Current eval (white's turn): 0.0
Make a move: e2e4
```

# Recent Updates

See [CHANGELOG.md](CHANGELOG.md) for recent changes and some random thoughts.

# Useful Links

This was my first time building a chess engine. Below is a list of useful links, which were invaluable on the journey.

## General Resources

- https://www.chessprogramming.org/Main_Page
- https://python-chess.readthedocs.io/en/latest/core.html#board

## Python Chess Repositories

- https://github.com/thomasahle/sunfish
- https://github.com/Disservin/python-chess-engine
- https://github.com/Alex2262/Antares
- https://github.com/Avo-k/skormfish

# License

[GNU GPLv3](LICENSE.md)
