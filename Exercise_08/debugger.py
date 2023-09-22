from types import FrameType, TracebackType
from typing import Any, Optional, Type
from debuggingbook.PerformanceDebugger import HitCollector, PerformanceDebugger

class HitCollector(HitCollector):
    def __init__(self, limit: int = 100000) -> None:
        super().__init__()
        self.limit = limit
        self.counter = limit

    def collect(self, frame: FrameType, event: str, arg: Any) -> None:
        super().collect(frame, event, arg)
        self.counter -= 1
        if self.counter == 0:
            raise OverflowError

class PerformanceDebugger(PerformanceDebugger):
    def __init__(self, collector_class: Type, log: bool = False):
        super().__init__(collector_class, log=log)
        self.overflow = False

    def is_overflow(self) -> bool:
        if self.overflow == True:
            return True
        else:
            return False

    def __exit__(self, exc_tp: Type, exc_value: BaseException, exc_traceback: TracebackType) -> Optional[bool]:
        if exc_tp == OverflowError:
            self.overflow = True
            self.add_collector(self.FAIL, self.collector)
            return self.is_overflow()
        return super().__exit__(exc_tp, exc_value, exc_traceback)


if __name__ == '__main__':
    def loop(x: int):
        x = x + 1
        while x > 0:
            pass

    with PerformanceDebugger(HitCollector) as debugger:
        loop(1)

    assert debugger.is_overflow()
    print(debugger)
