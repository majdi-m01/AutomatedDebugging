from .list_sum import *

def test_1():
    """+"""
    assert list_sum([]) == 0

def test_2():
    """+"""
    assert list_sum([2, 3, -5]) == 0

def test_3():
    """+"""
    assert list_sum(list(range(10))) == 45

def test_4():
    """-"""
    assert list_sum([None]) == 0

def test_5():
    """-"""
    assert list_sum([1, None]) == 1

def test_6():
    """-"""
    assert list_sum([1, None, 2, 3, None]) == 6
