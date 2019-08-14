from typing import Any, Callable, Generic, Mapping, Optional, TypeVar, Union
from abc import ABC, abstractmethod
from functools import wraps
import math
import collections

T = TypeVar("T", Any, None)

__all__ = ["Maybe", "Some", "Nothing"]


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
    def __init__(self, value: None, is_none: Optional[bool] = False) -> None:
        if not is_none:
            self._value = value
        super().__init__()

    @abstractmethod
    def get(self) -> T:
        pass

    @abstractmethod
    def get_or_else(self, value) -> T:
        pass

    @abstractmethod
    def is_some(self) -> bool:
        pass

    @abstractmethod
    def is_none(self) -> bool:
        pass


class Some(Maybe[T]):
    def __init__(self, value: T) -> None:
        super().__init__(value)

    def get(self) -> T:
        return self._value

    def get_or_else(self, value) -> T:
        return self.get()

    def is_some(self) -> bool:
        return True

    def is_none(self) -> bool:
        return False

    def __magic_wrapper(f):
        def wrapper(self, *args):
            return f(self.get(), *args)

        return wrapper

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Some):
            return self.get() == other.get()
        elif isinstance(other, Nothing):
            return False

        return self.get() == other

    @checkattr
    def __getitem__(self, key):
        try:
            return Some(self.get()[key])
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

    def __op_wrapper(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, other):
            # Normalize
            if isinstance(other, Some):
                other = other.get()
            try:
                return Some(func(self.get(), other))  # type: ignore
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
        if hasattr(self.get(), "__getattr__"):
            return self.get().__getattr__(attr)
        return self.get().__getattribute__(attr)

    def __str__(self) -> str:
        return "Some(%s)" % repr(self.get())

    __repr__ = __str__


class Nothing(Maybe[T]):
    def __init__(self) -> None:
        super().__init__(None, True)

    @staticmethod
    def __return_nothing(*args, **kwargs):
        return Nothing()

    def get(self) -> T:
        raise Exception("bad")

    def get_or_else(self, value) -> T:
        return value

    def is_some(self) -> bool:
        return False

    def is_none(self) -> bool:
        return True

    def __eq__(self, other: Any) -> bool:
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

    def __str__(self):
        return "Nothing()"

    __repr__ = __str__
