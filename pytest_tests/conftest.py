import pytest

from .. import Board


@pytest.fixture
def m8in3_fens():
    fname = 'pytest_tests/data/mate_in_3.txt'

    data = open(fname).read().splitlines()
    data = [d for d in data if d != '']
    valid_fens = []
    for datum in data:
        try:
            Board(datum)
            valid_fens.append(datum)
        except Exception as e:
            print(e)
            continue

    valid_fens.sort()
    return valid_fens


@pytest.fixture
def m8in2_fens():
    fname = 'pytest_tests/data/mate_in_2.txt'

    data = open(fname).read().splitlines()
    data = [d for d in data if d != '']
    valid_fens = []
    for datum in data:
        try:
            Board(datum)
            valid_fens.append(datum)
        except Exception as e:
            print(e)
            continue

    valid_fens.sort()
    return valid_fens
