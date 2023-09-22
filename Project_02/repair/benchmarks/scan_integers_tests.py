from .scan_integers import *

def test_1():
    """+"""
    assert scan_integers([]) == []

def test_2():
    """+"""
    assert scan_integers(['13', '0', '7']) == [13, 0, 7]

def test_3():
    """+"""
    assert scan_integers(['22', '100', 'foo']) == [22, 100]

def test_4():
    """-"""
    assert scan_integers(['13', '-1']) == [13]

def test_5():
    """-"""
    assert scan_integers(['9', '-1', '3']) == [9]

def test_6():
    """-"""
    assert scan_integers(['-1', '0', '2']) == []
