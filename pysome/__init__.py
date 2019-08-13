from typing import Any, Generic, Mapping, TypeVar, Union
from abc import ABC, abstractmethod
from functools import wraps
import math
import collections

T = TypeVar("T")


def checkattr(f):
    @wraps(f)
    def wrapper(self, *args):
        if not hasattr(self.get(), f.__name__):
            raise AttributeError(
                "%s does not have attribute %s" % (self.get().__class__, f.__name__)
            )
        return f(self, *args)

    return wrapper


class Maybe(Generic[T], ABC):
    def __init__(self, value: T) -> None:
        self._value = value
        super().__init__()

    @abstractmethod
    def get(self) -> T:
        pass

    @abstractmethod
    def or_else(self, value) -> T:
        pass

    def is_some(self) -> bool:
        return self._value is not None

    def is_none(self) -> bool:
        return self._value is None


class Something(Maybe[T]):
    def __init__(self, value: T) -> None:
        super().__init__(value)

    def get(self) -> T:
        return self._value

    def or_else(self, value) -> T:
        return self.get()

    def __magic_wrapper(f):
        def wrapper(self, *args):
            return f(self.get(), *args)

        return wrapper

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Something):
            return self.get() == other.get()
        elif isinstance(other, Nothing):
            return False

        return self.get() == other

    @checkattr
    def __getitem__(self, key):
        try:
            return maybe(self.get()[key])
        except KeyError:
            return Nothing()
        except IndexError:
            return Nothing()

    @checkattr
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

    def __add__(self, other):
        return self.get() + other

    def __sub__(self, other):
        return self.get() - other

    def __mul__(self, other):
        return self.get() * other

    def __div__(self, other):
        return self.get() / other

    def __str__(self) -> str:
        return "Something(%s)" % repr(self.get())

    __repr__ = __str__


class Nothing(Maybe[T]):
    def __init__(self) -> None:
        super().__init__(None)

    def get(self) -> T:
        raise Exception("bad")

    def or_else(self, value) -> T:
        return value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Nothing)

    def __str__(self):
        return "Nothing()"

    __repr__ = __str__


K = TypeVar("K")
V = TypeVar("V")

X = TypeVar("X")


def maybe(value: Union[Maybe[X], X]) -> Maybe[X]:
    if isinstance(value, Maybe):
        return value
    if value is not None:
        return Something(value)
    return Nothing()
