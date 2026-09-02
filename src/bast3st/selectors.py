from .base import Value
from .helpers import ArrayScope
from typing import Literal


class FutureVariable(Value):
    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name

    @property
    def name(self):
        return self._name

    def __repr__(self) -> str:
        return f"VAR({self.name!r})"


class FutureProperty(Value):
    def __init__(self, *, mode: Literal["array"], of, name: str) -> None:
        super().__init__()
        self._mode = mode
        self._of = of
        self._name = name

    def __repr__(self) -> str:
        if self._mode == "array" and self._name == "length":
            return f"{self._of!r}.length"
        raise ValueError(
            f"FutureProperty selector called with unsupported arguments: {self._mode} {self._of} {self._name}"
        )


# TODO: think if key should be allowed to be numeric `Value`
class FutureItem(Value):
    def __init__(self, array: FutureArray, key: int) -> None:
        self._array = array
        self._position = key

    @property
    def array(self) -> FutureArray:
        return self._array

    @property
    def position(self) -> int:
        return self._position

    def __repr__(self) -> str:
        return f"{self.array!r}[{self.position}]"


class FutureArray:
    """
    A :class:`FutureArray` represents a specific source of multiple
    values that are available – somewhere in the future – during the
    evaluation of a submission.
    """

    def __init__(self, kind: ArrayScope, name: str) -> None:
        super().__init__()
        self._kind: ArrayScope = kind
        self._name: str = name

    @property
    def kind(self) -> ArrayScope:
        return self._kind

    @property
    def name(self) -> str:
        return self._name

    def __getitem__(self, key: int) -> FutureItem:
        return FutureItem(self, key)

    @property
    def last(self) -> FutureItem:
        return self[-1]

    @property
    def length(self) -> FutureProperty:
        return FutureProperty(mode="array", of=self, name="length")

    @property
    def first(self) -> FutureItem:
        return self[0]

    def from_start1(self, onebased_n: int) -> FutureItem:
        assert onebased_n > 0, f"{onebased_n} should be at least 1"
        return self[onebased_n - 1]

    def from_end1(self, onebased_n: int) -> FutureItem:
        assert onebased_n > 0, f"{onebased_n} should be at least 1"
        return self[-onebased_n]

    def index1(self, onebased_n: int) -> FutureItem:
        assert onebased_n != 0, (
            "index1(1) means first element, index(-1) last, but index1(0) is undefined"
        )
        if onebased_n > 0:
            return self[onebased_n - 1]
        return self[-onebased_n]

    def __repr__(self) -> str:
        if self.kind == "io" and self.name == "output":
            return "OUTPUT"
        elif self.kind == "io" and self.name == "input":
            return "INPUT"
        elif self.kind == "list":
            return f"LIST({self.name!r})"
        return super().__repr__()


OUTPUT = FutureArray("io", "output")
INPUT = FutureArray("io", "input")


def LIST(name: str) -> FutureArray:
    return FutureArray("list", name)


def VAR(name: str) -> FutureVariable:
    return FutureVariable(name)
