# Changelog

Notable changes to this project will be documented in this file.

## [0.0.2] - Search Improvements + More

- Was undefeated in around 10 games against an 1800 rated human player in 30s games!

### Additional Features

#### Search

- Move from negamax to principal variation search
- Futility Pruning + Delta Pruning (qsearch)
- Move ordering slightly fixed/improved (and verified working)
- Null move pruning is working once more
- Overhaul to transposition tables to ensure more correct behavior

### General

- Main search fn no longer passes around moves (cleanup)
- PV updating moved to a utility function (cleanup)
- Search opening book path handling improved
- Pre-commit added for most files

## [0.0.1] - Initial Release

- Works with Bengal-Bot on Lichess and plays above 1000 rating - I'd call that a v0.01

### Feature List

- Opening Book Support

#### Evaluation

- Material Value
- Piece-Square Tables

#### Search

- Alpha Beta Pruning
- Transposition Tables via Zobrist Hashing
- Iterative Deepening
- Principal Variation Tracking
- Quiescence Search
- Null Move Heuristic (Pruning)
- Mate Distance Pruning
- Aspiration Windows [Bugged]

#### Move Ordering

- Principal Variation
- Hash (TT) Moves
- Killer Hueristic
- MVV/LVA

### Testing

- Search test on a variety of positions, especially testing en passant, promotions, checkmate (~30 tests)
- Mate in 2 (~221 tests)
- Mate in 3 (~500 tests)
- Perft (~30 tests)
