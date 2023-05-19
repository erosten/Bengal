# Changelog

Notable changes to this project will be documented in this file.


## [0.0.1]

### General
- Unused code/empty files cleaned up
- 

### Search
- Revamp of transposition table logic
- Removes Line/Node data structs in favor of tuples
- Subclass python-chess's Board to generate moves only as needed and in more optimal ordering
    - Huge speedup, able to reach depths up to 5-6 reasonably, up to 10 in a minute or two
- Add MATE checker to early return

#### Features
- 
#### Fixes
- Fix mating eval being flipped

### Evaluation

#### Features
- Notebooks displaying various existing evaluation functions
- Add mobility area/mobility bonuses

#### Fixes
- Fix for crash on eval when board is mate
- Fix for crash on eval when board is draw
- Fixed edge case on bishop xray
- Fixed king threat
- Fixed threat safe pawns
- Fixed pawn push threat
- Fixed hanging
- Fixed weak queen protection bonus
- Fixed supported
- Fixed doubled
- Fix semi-open file calc


