# to establish a baseline of search performance
# pure minimax - no TT, alpha beta, checkmate returning, etc.
# https://gist.github.com/peterellisjones/8c46c28141c162d1d8a0f0badbc9cff9
DATA = [
   {
      "depth":1,
      "nodes":8,
      "fen":"r6r/1b2k1bq/8/8/7B/8/8/R3K2R b KQ - 3 2",
      "comments": "black in check, but winning",
      "best_move": "h7h4, capture bishop"
   },
   {
      "depth":2,
      "nodes":192,
      "fen":"r6r/1b2k1bq/8/8/7B/8/8/R3K2R b KQ - 3 2",
      "comments": "black in check, but winning",
      "best_move": "h7h4, capture bishop, sees queen recap, but still winning"
   },
   {
      "depth":3,
      "nodes":8355,
      "fen":"r6r/1b2k1bq/8/8/7B/8/8/R3K2R b KQ - 3 2",
      "comments": "black in check, but winning",
      "best_move": "h7h4, sees capture of either rook after queen recap"
   },
   {
      "depth":1,
      "nodes":8,
      "fen":"8/8/8/2k5/2pP4/8/B7/4K3 b - d3 0 3",
      "comments": "black in check get out with ep cap",
      "best_move": "c4d3"
   },
   {
      "depth":1,
      "nodes":19,
      "fen":"r1bqkbnr/pppppppp/n7/8/8/P7/1PPPPPPP/RNBQKBNR w KQkq - 2 2",
      "comments": "opening, each side only 1 move",
      "best_move": "Not sure"
   },
   {
      "depth":1,
      "nodes":5,
      "fen":"r3k2r/p1pp1pb1/bn2Qnp1/2qPN3/1p2P3/2N5/PPPBBPPP/R3K2R b KQkq - 3 2",
      "comments": "black in check, pawn takes queen black winning",
      "best_move": "d7e6"
   },
   {
      "depth":1,
      "nodes":44,
      "fen":"2kr3r/p1ppqpb1/bn2Qnp1/3PN3/1p2P3/2N5/PPPBBPPP/R3K2R b KQ - 3 2",
      "comments": "pawn capture is best move at depth 1",
      "best_move": "f7e6"
   },
   {
      "depth":1,
      "nodes":39,
      "fen":"rnb2k1r/pp1Pbppp/2p5/q7/2B5/8/PPPQNnPP/RNB1K2R w KQ - 3 9",
      "comments": "ep promote with check best",
      "best_move": "d7c8q"
   },
   {
      "depth":1,
      "nodes":9,
      "fen":"2r5/3pk3/8/2P5/8/2K5/8/8 w - - 5 4",
      "comments": "white is lost",
      "best_move": "All bad, SF C3D3",
   },
   {
      "depth":3,
      "nodes":62379,
      "fen":"rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
      "comments": "ep capture promotion is best. its a sac, but white is up on depth 3",
      "best_move": "d7c8*"
   },
   {
      "depth":3,
      "nodes":89890,
      "fen":"r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
      "comments": "average midgame, white has advantage",
      "best_move": "not sure"
   },
   {
      "depth":6,
      "nodes":1134888,
      "fen":"3k4/3p4/8/K1P4r/8/8/8/8 b - - 0 1",
      "comments": "h5c5 is best, black is winning",
      "best_move": "h5c5"
   },
   {
      "depth":6,
      "nodes":1015133,
      "fen":"8/8/4k3/8/2p5/8/B2P2K1/8 w - - 0 1",
      "comments": "a2c4 capture, white is winning",
      "best_move": "a2c4"
   },
   {
      "depth":6,
      "nodes":1440467,
      "fen":"8/8/1k6/2b5/2pP4/8/5K2/8 b - d3 0 1",
      "comments": "ep cap is best, black advantage",
      "best_move": "c4d3"
   },
   {
      "depth":6,
      "nodes":661072,
      "fen":"5k2/8/8/8/8/8/8/4K2R w K - 0 1",
      "comments": "winning for white, mate far. best h1h7, cut off king",
      "best_move": "h1h7"
   },
   {
      "depth":6,
      "nodes":803711,
      "fen":"3k4/8/8/8/8/8/8/R3K3 w Q - 0 1",
      "comments": "winning for white, mate far. best a1a7, cut off king",
      "best_move": "a1a7"
   },
   {
      "depth":4,
      "nodes":1274206,
      "fen":"r3k2r/1b4bq/8/8/8/8/7B/R3K2R w KQkq - 0 1",
      "comments": "white huge advantage",
      "best_move": "a1a8"
   },
   {
      "depth":4,
      "nodes":1720476,
      "fen":"r3k2r/8/3Q4/8/8/5q2/8/R3K2R b KQkq - 0 1",
      "comments": "black is winning by a good margin",
      "best_move": "a8a1 is mate in 4, h8h1 is mate in 6"
   },
   {
      "depth":6,
      "nodes":3821001,
      "fen":"2K2r2/4P3/8/8/8/8/8/3k4 w - - 0 1",
      "comments": "winning for white, e7f8q, ep cap promote to queen",
      "best_move": "e7f8q"
   },
   {
      "depth":5,
      "nodes":1004658,
      "fen":"8/8/1P2K3/8/2n5/1q6/8/5k2 b - - 0 1",
      "comments": "cap on b3b6, black big advantage",
      "best_move": "b3b6"
   },
   {
      "depth":6,
      "nodes":217342,
      "fen":"4k3/1P6/8/8/8/8/K7/8 w - - 0 1",
      "comments": "winning for white, b7b8q, ep promote to queen",
      "best_move": "b7b8q"
   },
   {
      "depth":6,
      "nodes":92683,
      "fen":"8/P1k5/K7/8/8/8/8/8 w - - 0 1",
      "comments": "a6b5 or a5 draw, a7a8 n/b draw, q best (rook 2nd best)",
      "best_move": "a7a8q"
   },
   {
      "depth":6,
      "nodes":2217,
      "fen":"K1k5/8/P7/8/8/8/8/8 w - - 0 1",
      "comments": "draw over all moves",
      "best_move": "Shouldnt really matter"
   },
   {
      "depth":7,
      "nodes":567584,
      "fen":"8/k1P5/8/1K6/8/8/8/8 w - - 0 1",
      "comments": "mate for white - b5c6 or c7c8r, all other promos are draw", 
      "best_move": "[b5c6 or c7c8r]"
   },
   {
      "depth":4,
      "nodes":23527,
      "fen":"8/8/2k5/5q2/5n2/8/5K2/8 b - - 0 1",
      "comments": "mate in 3, depth 4 will not see. but big advantage black",
      "best_move": "f5h3 mate in 4, f5d3 mate in 3"
   },
      {
      "depth":2,
      "nodes":1649,
      "fen":"r2qk2r/pb4pp/1n2Pb2/2B2Q2/p1p5/2P5/2B2PPP/RN2R1K1 w - - 1 0",
      "comments": "sac queen for mate in 2 for white",
      "best_move": "Not sure at depth 2"
   },
      {
      "depth":3,
      "nodes":77229,
      "fen":"r2qk2r/pb4pp/1n2Pb2/2B2Q2/p1p5/2P5/2B2PPP/RN2R1K1 w - - 1 0",
      "comments": "sac queen for mate in 3 for white",
      "best_move": "f5g6"
   },
   {
      "nodes": 811573,
      "depth": 5,
      "fen": "8/8/2k5/5q2/5n2/8/5K2/8 b - - 0 1",
      "comments": "mate in 3, depth 5 should see",
      "best_move": "f3d3"
    }
]