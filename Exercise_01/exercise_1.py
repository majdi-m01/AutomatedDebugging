from typing import Tuple

LEN = 6
BASE = 16
OFFSET = 10
CHAR_a = 97
CHAR_f = 103
CHAR_A = 65
CHAR_F = 70
CHAR_0 = 48
CHAR_9 = 57

def check_lower(c: int) -> bool:
    return c in range(CHAR_a, CHAR_f + 1)

def check_upper(c: int) -> bool:
    return c in range(CHAR_A, CHAR_F + 1)

def check_number(c: int) -> bool:
    return c in range(CHAR_0, CHAR_9 + 1)

def check(c: int) -> bool:
    return check_lower(c) or check_upper(c) or check_number(c)

def convert_char(c: int) -> int:
    assert check(c)
    if check_lower(c):
        return c - CHAR_a + OFFSET
    elif check_upper(c):
        return c - CHAR_A + OFFSET
    else:
        return c - CHAR_0

def convert_byte(c1: int, c2: int) -> int:
    return convert_char(c1) * BASE + convert_char(c2)

def convert_string(s: str, i: int) -> int:
    return convert_byte(ord(s[i * 2]), ord(s[i * 2]))

def check_len(s) -> bool:
    return len(s) == LEN

def convert_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    assert check_len(hex_str)
    return (convert_string(hex_str, 0), convert_string(hex_str, 1), convert_string(hex_str, 2))