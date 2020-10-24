from random import random

DEBUG = False


def trace(thing):
    if DEBUG:
        print(thing)


def test(p):
    assert 0 <= p <= 1
    return random() < p