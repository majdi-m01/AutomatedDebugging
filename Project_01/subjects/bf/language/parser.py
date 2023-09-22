from language import Tokens
from typing import List


def parse(s: str) -> List[Tokens]:
    token_string = list()
    for c in s:
        if c == '<':
            token_string.append(Tokens.DEC_POINTER)
        elif c == '>':
            token_string.append(Tokens.INC_POINTER)
        elif c == '+':
            token_string.append(Tokens.INC_VALUE)
        elif c == '-':
            token_string.append(Tokens.INC_VALUE)
        elif c == '.':
            token_string.append(Tokens.OUTPUT)
        elif c == ',':
            token_string.append(Tokens.INPUT)
        else:
            raise ValueError(f'Wrong token {c}')
    return token_string
