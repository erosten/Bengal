# Bengal

Bengal is a traditional chess engine, written in Python. The goal of this project is to see how far a chess engine written in Python can really go.

With a sophisticated search function, a modified board representation based on the fantastic [python-chess](https://github.com/niklasf/python-chess) and boosted by pypy, [Bengal is currently around 1900 ELO on lichess](https://lichess.org/@/BengalBot).

# Features

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

# Changes

See [CHANGELOG.md](CHANGELOG.md)

# Useful Links

This was my first time delving into building a chess engine. Below is a list of useful links, which were invaluable on the journey.
