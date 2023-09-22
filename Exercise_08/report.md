# Report
## _By Majdi Maalej_

Example 1:
```sh
def ex_1(i: int):
    while i < 0:
        i = i + 1
```
This function terminates on all inputs. If i>=0, then the function is executed without the while loop. If i<0, then i will increment inside the while loop until it becomes more than zero, thus terminating.

Example 2:
```sh
def ex_2(i: int):
    while i != 1 and i != 0:
        i = i - 2
```
This function does not terminate for input of i<0. For example, if i=-1, then the while loop would not terminate, because the input is going to continue decrementing less and less, and the condition would still hold forever.
The following is the frequencies of each line collected by the debugger:
```sh
   5   2% def ex_2(i: int):
   6  51%     while i != 1 and i != 0:
   7  46%         i = i - 2
```

Example 3:
```sh
def ex_3(i: int, j: int):
    while i != j:
        i = i - 1
        j = j + 1
```
This function does not terminate for input of i<0 and j>0. For example, if i=-1 and j=1, then the while loop would not terminate, because i is going to continue getting smaller, and j is going to continue getting bigger, while the loop condition still holding forever (i!=j).
The following is the frequencies of each line collected by the debugger:
```sh
   9   0% def ex_3(i: int, j: int):
  10  33%     while i != j:
  11  33%         i = i - 1
  12  33%         j = j + 1
```

Example 4:
```sh
def ex_4(i: int):
    while i >= -5 and i <= 5:
        if i > 0:
            i = i - 1
        if i < 0:
            i = i + 1
```
This function does not terminate for input of i=0. The while loop would hold forever, since i=0 and -5<=0<=5, and inside the loop i=0 does not meet the conditions of both if statements, so there are no possible changes for the variable i, thus the while loop remains loops endlessly.
The following is the frequencies of each line collected by the debugger:
```sh
  14  33% def ex_4(i: int):
  15  66%     while i >= -5 and i <= 5:
  16   0%         if i > 0:
  17   0%             i = i - 1
  18   0%         if i < 0:
  19   0%             i = i + 1
```

Example 5:
```sh
def ex_5(i: int):
    while i < 10:
        j = i
        while j > 0:
            j = j + 1
        i = i + 1
```
This function does not terminate for input of 1<=i<=9. Let's say i=7, then the inner while loop would iterate forever, since j=7 >0, and inside that loop, the variable j is going to continue incrementing, thus j would remain greater than zero, and condition continues to hold endlessly.
The following is the frequencies of each line collected by the debugger:
```sh
  21   0% def ex_5(i: int):
  22   0%     while i < 10:
  23   0%         j = i
  24  49%         while j > 0:
  25  49%             j = j + 1
  26   0%         i = i + 1
```

Example 6:
```sh
def ex_6(i: int):
    c = 0
    while i >= 0:
        j = 0
        while j <= i - 1:
            j = j + 1
            c = c + 1
        i = i - 1
```
This function would terminate on all inputs. If i<0, then the function would execute completely without going inside the outer while loop. If i>=0, then the outer while loop would get executed and eventually ends too. The inner while loop would get executed if j<=i-1, and indeed it would complete executing, since j continues to increment and at some point j would be greater than i-1, and thus the inner while loop is done.