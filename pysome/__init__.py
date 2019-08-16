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

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")

__all__ = ["Maybe", "Some", "Nothing", "maybe"]


def checkattr(f):
    @wraps(f)
    def wrapper(self, *args):
        if not hasattr(self.get(), f.__name__):
            raise AttributeError(
                "%s does not have attribute %s"
                % (self.get().__class__, f.__name__)
            )
        return f(self, *args)

    return wrapper


class Maybe(Generic[T], ABC):
    def __init__(self, value, is_none=False):
        if not is_none:
            self._value = value
        super().__init__()

    @abstractmethod
    def get(self) -> Union[T, NoReturn]:
        pass

    @abstractmethod
    def or_else(self, value: T) -> T:
        pass

    @abstractmethod
    def is_some(self):
        pass

    @abstractmethod
    def is_none(self):
        pass

    @abstractmethod
    def __add__(self, other: Any) -> Any:
        pass

    @abstractmethod
    def comb(self, *funcs: Callable[['Maybe'], 'Maybe']) -> 'Maybe':
        pass


class Some(Maybe[T]):
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

    def comb(self, *funcs: Callable[[T], Maybe]) -> Maybe:
        if len(funcs) == 1:
            print(funcs[0])
            return funcs[0](self)
        return funcs[0](self).comb(funcs[1:])

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

    @checkattr
    def __getitem__(self, key: K) -> Maybe[V]:
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

    def __op_wrapper(func):
        @wraps(func)
        def wrapper(self, other: Any) -> Maybe[Any]:
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
    __radd__ = __add__
    __sub__ = __op_wrapper(lambda x, y: x - y)
    __rsub__ = __op_wrapper(lambda x, y: y - x)
    __mul__ = __op_wrapper(lambda x, y: x * y)
    __rmul__ = __mul__
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
        return "Some(%s)" % repr(self.get())

    __repr__ = __str__


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
        return "Nothing()"

    __repr__ = __str__

def maybe(value):
    if value == Nothing():
        return Nothing()
    return Some(value)
