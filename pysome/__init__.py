from typing import Any, Generic, Mapping, Optional, TypeVar, Union
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
                "%s does not have attribute %s"
                % (self.get().__class__, f.__name__)
            )
        return f(self, *args)

    return wrapper


class Maybe(Generic[T], ABC):
    def __init__(self, value: T, is_none: Optional[bool] = False) -> None:
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

    def __add__(self, other: Union[Maybe[T], T]):
        # Normalize
        if isinstance(other, Some):
            other = other.get()

        try:
            return Some(self.get() + other)  # type: ignore
        except AttributeError:
            return Nothing()
        except TypeError:
            return Nothing()

    def __sub__(self, other: Union[Maybe[T], T]):
        # Normalize
        if isinstance(other, Some):
            other = other.get()

        try:
            return Some(self.get() - other)  # type: ignore
        except AttributeError:
            return Nothing()
        except TypeError:
            return Nothing()

    def __mul__(self, other: Union[Maybe[T], T]):
        # Normalize
        if isinstance(other, Some):
            other = other.get()

        try:
            return Some(self.get() * other)  # type: ignore
        except AttributeError:
            return Nothing()
        except TypeError:
            return Nothing()

    def __div__(self, other: Union[Maybe[T], T]):
        # Normalize
        if isinstance(other, Some):
            other = other.get()

        try:
            return Some(self.get() / other)
        except AttributeError:
            return Nothing()
        except TypeError:
            return Nothing()

    def __str__(self) -> str:
        return "Some(%s)" % repr(self.get())

    __repr__ = __str__


class Nothing(Maybe[T]):
    def __init__(self) -> None:
        super().__init__(None, True)

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

    def __str__(self):
        return "Nothing()"

    __repr__ = __str__


a: Maybe[str] = Some('str')
b: Maybe[int] = Some(1)
