from .char_index import *

def test_1():
    """+"""
    assert char_index('ASE', 'A') == 0

def test_2():
    """+"""
    assert char_index('FSE', 'A') == None

def test_3():
    """-"""
    assert char_index('*SE', 'A') == 0

def test_4():
    """-"""
    assert char_index('F*E', 'E') == 1