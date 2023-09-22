from language import Tokens
from language.parser import parse


def interpret(program: str, input_stream: bytes) -> bytes:
    token_string = parse(program)
    output_stream = b''
    mem = {0: 0}
    ptr = 0
    pos = 0
    while pos < len(token_string):
        if token_string[pos] == Tokens.INC_VALUE:
            mem[ptr] += 1
            pos += 1
        elif token_string[pos] == Tokens.DEC_VALUE:
            mem[ptr] -= 1
            pos += 1
        elif token_string[pos] == Tokens.INC_POINTER:
            ptr += 1
            pos += 1
        elif token_string[pos] == Tokens.DEC_POINTER:
            ptr -= 1
            pos += 1
        elif token_string[pos] == Tokens.OUTPUT:
            output_stream += mem[ptr].to_bytes(1, 'little')
            pos += 1
        elif token_string[pos] == Tokens.INPUT:
            mem[ptr], input_stream = input_stream[0], input_stream[1:]
            pos += 1
        if ptr not in mem:
            mem[ptr] = 0
    return output_stream
