from typing import (
    Any,
    Callable,
    cast,
    Generic,
    Mapping,
    NoReturn,
    Optional,
    TypeVar,
    Union,
)
from abc import ABC, abstractmethod
from functools import wraps
import math
import collections

from util import *

__all__ = ["Maybe", "Some", "Nothing", "maybe"]


class Maybe(Generic[T], ABC):
    """
    Generic class and type for the pysome Maybe object. Two classes inherit from
    this abstract class: Some and Nothing.
    """

    def __init__(self, value, is_none=False):
        if not is_none:
            self._value = value
        super().__init__()

    @abstractmethod
    def get(self) -> Union[T, NoReturn]:
        """
        Get the value that is stored if it is a `Some` object, or throw an error
        if it is `Nothing` object. Should only be used if you know that it is a
        `Some` object. If you are unsure, you can use `Maybe.or_else()`.
        """
        pass

    @abstractmethod
    def or_else(self, value: T) -> T:
        """
        Get the value that is stored if it is a `Some` object, or return `value` if it is a `Nothing` object.

            value: T
                - A default value to be returned if it is a Nothing class
        """
        pass

    def some_or_else(self, value: T) -> "Maybe[T]":
        return maybe(self.or_else(value))

    @abstractmethod
    def is_some(self) -> bool:
        """
        Return whether or not the class is `Some`. Equivalent to `isinstnace(self, Some).
        """
        pass

    @abstractmethod
    def is_none(self) -> bool:
        """
        Return whether or not the class is `Some`. Equivalent to `isinstnace(self, Nothing).
        """
        pass

    @abstractmethod
    def comb(self, *funcs: Callable[["Maybe"], "Maybe"]) -> "Maybe":
        """
        Given a list of functions, call each function iteratively on self and
        return the result. It should be noted that the following two are
        equivalent. The functions are assumed to be "maybe" functions, in that
        they take in a Maybe object and return a Maybe object. If you have a
        function that is not of that type, you can use the @maybefunction
        wrapper to convert it.

        > something.comb(f1, f2, f3)
        > something.comb(f1).comb(f2).comb(f3)

            funcs: Callable[[Maybe], Maybe]
                - A "maybe" function that takes in a Maybe object and returns
                a Maybe object.
        """
        pass


class Some(Maybe[T]):
    """
    A class that contains something. While it is possible to directly instatiate
    a `Some` object, you should instead use the `maybe()` function.
    """

    def __init__(self, value):
        super().__init__(value)

    def get(self) -> T:
        return self._value

    def or_else(self, value: T) -> T:
        return self.get()

    def is_some(self):
        return True

    def is_none(self):
        return False

    def comb(self, *funcs: Callable[[Maybe[T]], Maybe[U]]) -> Maybe[U]:
        value = self.get()
        for func in funcs:
            value = func(value)
            if value == Nothing():
                return value
        return value

    def __magic_wrapper(f):
        def wrapper(self, *args):
            return f(self.get(), *args)

        return wrapper

    def __eq__(self, other):
        if isinstance(other, Some):
            return self.get() == other.get()
        elif isinstance(other, Nothing):
            return False

        return self.get() == other

    def __getitem__(self, key: K) -> Maybe[V]:
        try:
            return maybe(self.get()[key])
        except KeyError:
            return Nothing()
        except IndexError:
            return Nothing()
        except TypeError:
            return Nothing()

    def __setitem__(self, key, value):
        self.get()[key] = value

    __int__ = __magic_wrapper(int)
    __complex__ = __magic_wrapper(complex)
    __float__ = __magic_wrapper(float)
    __bool__ = __magic_wrapper(bool)
    __round__ = __magic_wrapper(round)
    __trunc__ = __magic_wrapper(math.trunc)
    __floor__ = __magic_wrapper(math.floor)
    __ceil__ = __magic_wrapper(math.ceil)
    __len__ = __magic_wrapper(len)
    __hash__ = __magic_wrapper(hash)

    def __op_wrapper(func):
        @wraps(func)
        def wrapper(self, other: Any) -> Maybe:
            # Normalize
            if isinstance(other, Some):
                other = other.get()
            try:
                return maybe(func(self.get(), other))  # type: ignore
            except TypeError:
                return Nothing()
            # Division case (I don't know how much overhead this adds)
            except ZeroDivisionError:
                return Nothing()

        return wrapper

    __add__ = __op_wrapper(lambda x, y: x + y)
    __radd__ = __op_wrapper(lambda x, y: y + x)
    __sub__ = __op_wrapper(lambda x, y: x - y)
    __rsub__ = __op_wrapper(lambda x, y: y - x)
    __mul__ = __op_wrapper(lambda x, y: x * y)
    __rmul__ = __op_wrapper(lambda x, y: y * x)
    __truediv__ = __op_wrapper(lambda x, y: x / y)
    __rtruediv__ = __op_wrapper(lambda x, y: y / x)

    def __getattr__(self, attr):
        try:
            if hasattr(self.get(), "__getattr__"):
                return self.get().__getattr__(attr)
            return self.get().__getattribute__(attr)
        except AttributeError:
            return Nothing()

    def __str__(self):
        return str(self.get())

    def __repr__(self):
        return "Some(%s)" % repr(self.get())


class Nothing(Maybe[T]):
    def __init__(self):
        super().__init__(None, True)

    @staticmethod
    def __return_nothing(*args, **kwargs):
        return Nothing()

    def get(self) -> NoReturn:
        raise Exception("bad")

    def or_else(self, value: T) -> T:
        return value

    def is_some(self):
        return False

    def is_none(self):
        return True

    def comb(self, *funcs: Callable[[T], Maybe]) -> Maybe:
        return self

    def __eq__(self, other):
        return isinstance(other, Nothing)

    # All operators should return Nothing
    __add__ = __return_nothing
    __radd__ = __return_nothing
    __sub__ = __return_nothing
    __rsub__ = __return_nothing
    __mul__ = __return_nothing
    __rmul__ = __return_nothing
    __truediv__ = __return_nothing
    __rtruediv__ = __return_nothing
    __getitem__ = __return_nothing
    __getattr__ = __return_nothing
    __call__ = __return_nothing

    def __str__(self):
        return "None"

    def __repr__(self):
        return "Nothing"


def maybe(value):
    if value == Nothing():
        return Nothing()
    elif isinstance(value, Some):
        return value
    return Some(value)
