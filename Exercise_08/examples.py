def ex_1(i: int):
    while i < 0:
        i = i + 1

def ex_2(i: int):
    while i != 1 and i != 0:
        i = i - 2

def ex_3(i: int, j: int):
    while i != j:
        i = i - 1
        j = j + 1

def ex_4(i: int):
    while i >= -5 and i <= 5:
        if i > 0:
            i = i - 1
        if i < 0:
            i = i + 1

def ex_5(i: int):
    while i < 10:
        j = i
        while j > 0:
            j = j + 1
        i = i + 1

def ex_6(i: int):
    c = 0
    while i >= 0:
        j = 0
        while j <= i - 1:
            j = j + 1
            c = c + 1
        i = i - 1