from functools import reduce
from typing import Iterable, List, TypeVar

T = TypeVar("T")


def flatten(list_of_lists: Iterable[Iterable[T]]) -> List[T]:
    return reduce(lambda acc, lst: acc + list(lst), list_of_lists, [])
