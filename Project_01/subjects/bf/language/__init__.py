import enum


class Tokens(enum.Enum):
    INC_POINTER = 0
    DEC_POINTER = 1
    INC_VALUE = 2
    DEC_VALUE = 3
    OUTPUT = 4
    INPUT = 5
    LOOP_BEGIN = 6
    LOOP_END = 7
