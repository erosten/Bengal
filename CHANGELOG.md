# Changelog

Notable changes to this project will be documented in this file.

## [0.0.4] - Perfecting Performance

## [0.0.3] - More Search Improvements

The goal of this version was to release the bot in the wild on Lichess via AWS, as well as explore
Late move reductions, add a little more evaluation intelligence, as well as some performance boosts and bugfixes.
A key find is that these pruning methods lead to reduced performance via the eye test on Lichess.
The next release will focus on how to evaluate the performance of Bengal and measure improvements from additional search features/improvements.

#### General

- Rated about 1900 on Lichess Bullet/Blitz/Rapid - bot is now live all the time!
- README added
- Tested with pypy and has a huge speedup
- Bugfix for the same move potentially being searched multiple times
- Remove older search options
- Codebase-wide logger in utils
- Cleanup on comments and unused files in repo
- Bengal-bot updated

#### Search

- History Hueristic for non-capture moves
  - Initial tests show improvement in node count/speed
- Improved draw detection
  - As a side effect, improved performance by not having to check for repetitions in eval
- Mate pruning on actual nodes instead of only scores (faster on mate detection)
- Full NMP is back (>= beta, check for one major piece)
- Futility/Delta Pruning not currently viable while eval is lagging behind
  - Leave commented for now for later testing
- Late Move Reductions

#### Eval

- Most of pawn eval is implemented

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
