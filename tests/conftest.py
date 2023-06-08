import pytest
import json

from .. import Board



def load_fens(fname):
    data = open(fname).read().splitlines()
    data = [d for d in data if d != '']
    valid_fens = []
    for datum in data:
        try:
            Board(datum)
            valid_fens.append(datum)
        except ValueError:
            continue

    valid_fens.sort()
    return valid_fens    

@pytest.fixture
def m8in3_fens():
    return load_fens('tests/data/mate_in_3.txt')


@pytest.fixture
def m8in2_fens():
    return load_fens('tests/data/mate_in_2.txt')

@pytest.fixture
def perft_fen_data():
    fname = 'tests/data/search_test_data.json'
    with open(fname, 'r') as f:
        return json.load(f)
    

@pytest.fixture
def wac200():
    fname = 'tests/data/wac_200.epd'
    with open(fname, 'r') as f:
        epds = [line.strip() for line in f.readlines()]
    
    return epds