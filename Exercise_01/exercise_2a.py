import inspect
import sys
from types import FrameType
from typing import Callable, TextIO, Any
from debuggingbook.Tracer import Tracer

from exercise_2 import *


def param_names(func: Callable):
    return inspect.getfullargspec(func).args


class RecursiveTracer(Tracer):
    fibIndentation = 0
    mergeIndentation = 0

    def __init__(self, func: Callable, file: TextIO = sys.stdout) -> None:
        self.func: Callable = func
        super().__init__(file=file)

    def traceit(self, frame: FrameType, event: str, arg: Any) -> None:
        if fib.__name__:
            if 'n' in param_names(self.func):
                value_of_n = frame.f_locals['n']
                if 'call' == event:
                    self.log(f"{'  ' * RecursiveTracer.fibIndentation}call with n = {repr(value_of_n)}")
                    RecursiveTracer.fibIndentation += 1
                if 'return' == event:
                    RecursiveTracer.fibIndentation -= 1
                    self.log(f"{'  ' * RecursiveTracer.fibIndentation}return {repr(arg)}")
        if merge_sort.__name__:
            if 'arr' and 'l' and 'r' in frame.f_locals:
                value_of_arr = frame.f_locals['arr']
                value_of_l = frame.f_locals['l']
                value_of_r = frame.f_locals['r']
                if "merge" == frame.f_code.co_name:
                    pass
                else:
                    if 'call' == event:
                        self.log(f"{'  ' * RecursiveTracer.mergeIndentation}call with arr = {repr(value_of_arr)}, l = {repr(value_of_l)}, r = {repr(value_of_r)}")
                        RecursiveTracer.mergeIndentation += 1
                    if 'return' == event:
                        RecursiveTracer.mergeIndentation -= 1
                        self.log(f"{'  ' * RecursiveTracer.mergeIndentation}return {repr(arg)}")


######## Tests ########

if __name__ == '__main__':
    with RecursiveTracer(func=fib):
        fib(4)

    # the following is the expected log output:
    expected = """
call with n = 4
  call with n = 3
    call with n = 2
      call with n = 1
      return 1
      call with n = 0
      return 0
    return 1
    call with n = 1
    return 1
  return 2
  call with n = 2
    call with n = 1
    return 1
    call with n = 0
    return 0
  return 1
return 3
"""

    with RecursiveTracer(func=merge_sort):
        arr = [12, 11, 13, 5, 6, 7]
        merge_sort(arr, 0, len(arr) - 1)

    # the following is the expected log output:
    expected = """
call with arr = [12, 11, 13, 5, 6, 7], l = 0, r = 5
  call with arr = [12, 11, 13, 5, 6, 7], l = 0, r = 2
    call with arr = [12, 11, 13, 5, 6, 7], l = 0, r = 1
      call with arr = [12, 11, 13, 5, 6, 7], l = 0, r = 0
      return [12, 11, 13, 5, 6, 7]
      call with arr = [12, 11, 13, 5, 6, 7], l = 1, r = 1
      return [12, 11, 13, 5, 6, 7]
    return [11, 12, 13, 5, 6, 7]
    call with arr = [11, 12, 13, 5, 6, 7], l = 2, r = 2
    return [11, 12, 13, 5, 6, 7]
  return [11, 12, 13, 5, 6, 7]
  call with arr = [11, 12, 13, 5, 6, 7], l = 3, r = 5
    call with arr = [11, 12, 13, 5, 6, 7], l = 3, r = 4
      call with arr = [11, 12, 13, 5, 6, 7], l = 3, r = 3
      return [11, 12, 13, 5, 6, 7]
      call with arr = [11, 12, 13, 5, 6, 7], l = 4, r = 4
      return [11, 12, 13, 5, 6, 7]
    return [11, 12, 13, 5, 6, 7]
    call with arr = [11, 12, 13, 5, 6, 7], l = 5, r = 5
    return [11, 12, 13, 5, 6, 7]
  return [11, 12, 13, 5, 6, 7]
return [5, 6, 7, 11, 12, 13]
"""