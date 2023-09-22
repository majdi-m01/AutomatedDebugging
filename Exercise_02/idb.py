from inspect import getsourcelines
import sys
from types import CodeType, FrameType
from typing import TextIO, Set, Optional, Any, Dict

from debuggingbook.Debugger import Debugger

from test import debug_main


class CallInfo:
    def __init__(self, caller: CodeType, line_no: int) -> None:
        self.caller = caller
        self.loc = line_no

    def __repr__(self) -> str:
        head = f'File "{self.caller.co_filename}", line {self.loc}, in {self.caller.co_name}'
        lines, start = getsourcelines(self.caller)
        code = lines[self.loc - start].strip()
        return f'{head}\n  {code}'


class Debugger(Debugger):
    """Interactive Debugger"""

    def break_command(self, arg: str = "") -> None:
        """Set a breakpoint in given line. If no line is given, list all breakpoints"""
        source_lines, line_number = getsourcelines(self.frame.f_code)
        if arg:
            try:
                if line_number + len(source_lines) - 1 < int(arg) or int(arg) < line_number:
                    raise Exception(
                        f"Line number {arg} out of bound ({line_number}-{line_number + len(source_lines) - 1})")
                self.breakpoints.add(int(arg))
            except ValueError:
                print(f"Expect a line number, but found '{arg}'")
            except Exception as err:
                print(f"{str(err)}")
        self.log("Breakpoints:", self.breakpoints)

    def delete_command(self, arg: str = "") -> None:
        """Delete breakpoint in line given by `arg`. Without given line, clear all breakpoints"""
        if arg:
            try:
                self.breakpoints.remove(int(arg))
            except KeyError:
                self.log(f"No such breakpoint: {arg}")
            except ValueError:
                print(f"Expect a line number, but found '{arg}'")
        else:
            self.breakpoints = set()
        self.log("Breakpoints:", self.breakpoints)

    def assign_command(self, arg: str) -> None:
        """Use as 'assign VAR=VALUE'. Assign VALUE to local variable VAR."""
        sep = arg.find('=')
        if sep > 0:
            try:
                var = arg[:sep].strip()
                if not var.isidentifier():
                    raise SyntaxError(f"'{var}' is not an identifier")
                if var not in self.local_vars:
                    print(f"Warning: a new variable {var} is created")
            except SyntaxError as err:
                print(f"{err.__class__.__name__}: {str(err)}")
            expr = arg[sep + 1:].strip()
        else:
            self.help_command("assign")
            return

        vars = self.local_vars
        try:
            if var.isidentifier():
                vars[var] = eval(expr, self.frame.f_globals, vars)
        except Exception as err:
            self.log(f"{err.__class__.__name__}: {err}")

    def __init__(self, *, file: TextIO = sys.stdout) -> None:
        """Create a new interactive debugger."""
        self.stepping: bool = True
        self.breakpoints: Set[int] = set()
        self.interact: bool = True

        self.frame: FrameType
        self.event: Optional[str] = None
        self.arg: Any = None

        self.local_vars: Dict[str, Any] = {}

        self.finishing: bool = False
        self.nexting: bool = False
        self.count: int = 0

        super().__init__(file=file)

    def stop_here(self) -> bool:
        """Return True if we should stop"""
        if self.nexting:
            if self.count == 0 and (self.event == "line" or self.event == "return"):
                self.stepping = True
            else:
                self.stepping = False
            if self.event == "call":
                self.count += 1
            elif self.event == "return":
                self.count -= 1
        if self.finishing:
            if self.event == "call" or self.event == "line":
                self.stepping = False
            elif self.event == "return" and self.count == 0:
                self.stepping = True
            if self.event == "call":
                self.count += 1
            elif self.event == "return":
                self.count -= 1
        return self.stepping or self.frame.f_lineno in self.breakpoints

    def next_command(self, arg: str = "") -> None:
        """When stopped at a function call, the entire call is executed, stopping when the function returns"""
        self.interact = False
        self.nexting = True
        self.stepping = False
        self.finishing = False

    def finish_command(self, arg: str = "") -> None:
        """Resume execution until the current function returns"""
        self.interact = False
        self.finishing = True
        self.stepping = False
        self.nexting = False

    def where_command(self, arg: str = "") -> None:
        """Print the stack trace"""
        frame = self.frame
        logs = []
        while frame.f_code.co_name != '<module>':
            call = CallInfo(frame.f_code, frame.f_lineno)
            logs += [call.__repr__()]
            frame = frame.f_back
        self.log("Traceback (most recent call last):")
        #logs = logs[-2:]
        for i in logs[::-1]:
            self.log(i)

    def continue_command(self, arg: str = "") -> None:
        """Resume execution"""
        self.stepping = False
        self.interact = False
        self.nexting = False
        self.finishing = False

    def step_command(self, arg: str = "") -> None:
        """Execute up to the next line"""
        self.stepping = True
        self.interact = False
        self.nexting = False
        self.finishing = False

    def quit_command(self, arg: str = "") -> None:
        """Finish execution"""
        self.breakpoints = set()
        self.stepping = False
        self.interact = False
        self.finishing = False
        self.nexting = False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("No input file", file=sys.stderr)
        exit(1)

    module_name = sys.argv[1][:-3]  # remove .py
    exec(f"from {module_name} import debug_main")

    with Debugger():
        debug_main()
