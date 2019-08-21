""" A collection of "maybe" functions. Functions of the signature Callable[[Maybe[T]], Maybe[U]]"""
from typing import Any, Callable, Dict, List
from util import *
from maybe import Maybe, Nothing, maybe
from functools import wraps


def maybefunction(f: Callable[[T], U]) -> Callable[[Maybe[T]], Maybe[U]]:
    """
    A wrapper that takes a function and "maybifies" it.
    """

    @wraps(f)
    def wrapper(value: Maybe[T]) -> Maybe[U]:
        try:
            return maybe(f(value))
        except Exception:
            return Nothing()

    return wrapper


@maybefunction
def maybestr(value: Any) -> str:
    """
    A "maybified" version of the str() function.
    """
    return str(value)


@maybefunction
def maybeint(value: Any) -> int:
    """
    A "maybified" version of the int() function.
    """
    return int(value)


@maybefunction
def maybefloat(value: Any) -> float:
    """
    A "maybified" version of the float() function.
    """
    return float(value)


@maybefunction
def maybebool(value: Any) -> bool:
    """
    A "maybified" version of the bool() function.
    """
    return bool(value)


@maybefunction
def maybelen(value: Any) -> int:
    """
    A "maybified" version of the len() function.
    """
    return len(value)


@maybefunction
def maybedict(value: Any) -> Dict:
    return dict(value)

@maybefunction
def maybelist(value: Any) -> List:
    return list(value)
