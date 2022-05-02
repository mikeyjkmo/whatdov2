from typing import Callable, TypeVar

T = TypeVar("T")


def pipe(*fns: Callable[[T], T]) -> Callable[[T], T]:
    def _call(initial_task: T) -> T:
        res = initial_task
        for fn in fns:
            res = fn(res)
        return res
    return _call
