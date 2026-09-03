from __future__ import annotations

from typing import NoReturn, Literal
import abc
from string import templatelib
import itertools
import typing

type ArrayScopeT = Literal["io", "list"]
type RelationT = Literal["==", "!=", "<=", ">=", "<", ">"]
"""A comparison operator string to specify the desired relation"""

type SelectorOpcodeT = Literal["var", "arrayitem", "arrayprop"]
type ContainOpcodeT = Literal["contain_onlynum", "contain_num", "contain_text"]


NO_BOOL_ON_CRITERION = "A criterion shouldn't be used in Python boolean expressions, you can't use Pythons and, or and not keywords on it, but & (all_of(...)), | (any_of(...)) and ~ (.negated) work!"


class DecisionEntity(abc.ABC):
    def _ar(self, *args, **kwargs) -> str:
        """
        This should format custom arguments together with the ones of the base class
        into a comma-separated string

        (stands for _arg_repr)
        """
        fmt_args = [repr(a) for a in args]
        fmt_kwargs = [f"{k}={v!r}" for (k, v) in kwargs.items()]
        return ", ".join(fmt_args + fmt_kwargs)

    def _repr(self, *args, **kwargs) -> str:
        """Utility that returns a string of class-name(self._ar(*args, **kwargs))"""
        return f"{self.__class__.__name__}({self._ar(*args, **kwargs)})"

    def __bool__(self) -> NoReturn:
        raise TypeError("You can't use bool(...) on decision entities")

    def __format__(self, _: str, /) -> NoReturn:
        raise TypeError(
            "Decision entities should never be used in format string, use Python 3.14 t-strings instead"
        )


################################
# Future values
################################


class Value(DecisionEntity, abc.ABC):
    @typing.overload
    @classmethod
    def of(cls, val: IntoValue) -> Value: ...

    @typing.overload
    @classmethod
    def of(cls, val: IntoValue | None) -> Value | None: ...

    @classmethod
    def of(cls, val):
        """Exactly like :any:`ofStrict` but returns `None` if input is `None`"""
        if val is not None:
            return cls.ofStrict(val)
        return None

    @classmethod
    def ofStrict(cls, val: IntoValue) -> Value:
        """
        Converts a set of supported types into sub-classes of :class:`Value`

        :raise TypeError: If the input is of a not-supported type
        """
        if isinstance(val, Value):
            return val
        elif isinstance(val, (str, int, bool, float)):
            return LitValue(val)
        elif isinstance(val, templatelib.Template):
            return _concat_from_template(val)
        raise TypeError(
            f"Unknown type for Value.of: {type(val)}, maybe you shouln't use this as a value ({val!r})"
        )

    def __eq__(self, value: IntoValue, /) -> Criterion:  # type: ignore
        return compare.eq(self, value)

    def __ne__(self, value: IntoValue, /) -> Criterion:  # type: ignore
        return compare.neq(self, value)

    def __lt__(self, value: IntoValue, /) -> Criterion:
        return compare.lt(self, value)

    def __gt__(self, value: IntoValue, /) -> Criterion:
        return compare.gt(self, value)

    def __le__(self, value: IntoValue, /) -> Criterion:
        return compare.le(self, value)

    def __ge__(self, value: IntoValue, /) -> Criterion:
        return compare.ge(self, value)

    def __add__(self, other: IntoValue, /) -> Transformed:
        return Transformed("add", self, Value.ofStrict(other))

    def __sub__(self, other: IntoValue, /) -> Transformed:
        return Transformed("sub", self, Value.ofStrict(other))

    def __mul__(self, other: IntoValue, /) -> Transformed:
        return Transformed("mul", self, Value.ofStrict(other))

    def __truediv__(self, other: IntoValue, /) -> Transformed:
        return Transformed("truediv", self, Value.ofStrict(other))

    def __floordiv__(self, other: IntoValue, /) -> Transformed:
        # // operator (integer division)
        return Transformed("floordiv", self, Value.ofStrict(other))

    def __mod__(self, other: IntoValue, /) -> Transformed:
        return Transformed("mod", self, Value.ofStrict(other))

    def __pow__(self, other: IntoValue, /) -> Transformed:
        return Transformed("pow", self, Value.ofStrict(other))

    def __neg__(self, /) -> Transformed:
        return Transformed("neg", self)

    def __floor__(self, /) -> Transformed:
        return Transformed("floor", self)

    def __ceil__(self, /) -> Transformed:
        return Transformed("ceil", self)

    def __round__(self, /) -> Transformed:
        return Transformed("round", self)

    def __abs__(self, /) -> Transformed:
        return Transformed("abs", self)

    def contains_text(
        self, val: IntoTextValue, *, sample_expected: IntoTextValue | None = None
    ) -> Criterion:
        return Contained(
            sub=val, sup=self, mode="contain_text", sample_expected=sample_expected
        )

    def contains_only_this_number(
        self, val: IntoValue, *, sample_expected: IntoTextValue | None = None
    ) -> Criterion:
        return Contained(
            sub=val, sup=self, mode="contain_onlynum", sample_expected=sample_expected
        )

    def contains_this_number(
        self, val: IntoValue, *, sample_expected: IntoTextValue | None = None
    ) -> Criterion:
        return Contained(
            sub=val, sup=self, mode="contain_num", sample_expected=sample_expected
        )

    def text_is_contained_in(
        self, val: IntoTextValue, *, sample_expected: IntoTextValue | None = None
    ) -> Criterion:
        return Contained(
            sub=self, sup=val, mode="contain_text", sample_expected=sample_expected
        )

    def pipe(
        self, operation: Transformation, *operations: Transformation
    ) -> Transformed:
        """
        Execute a sequence of transformations in order on this value
        and return the final result. The value itself is the input to
        the first :class:`Transformation` and every further
        :class:`Transformation` gets the output of the last as input.
        The last :class:`Transformation`'s output will be returned.
        """
        val = operation.on(self)
        for op in operations:
            val = op.on(val)
        return val

    def to_upper(self) -> Transformed:
        return self.pipe(to_upper)

    def to_lower(self) -> Transformed:
        return self.pipe(to_lower)

    def trim_start(self) -> Transformed:
        return self.pipe(trim_start)

    def trim_end(self) -> Transformed:
        return self.pipe(trim_end)

    def trim(self) -> Transformed:
        return self.pipe(trim)


type IntoTextValue = str | templatelib.Template | Value
"""Any type that can be converted into a :class:`Value` and is likely a text"""

type IntoValue = IntoTextValue | float | int | bool
"""Any type that can be converted into a :class:`Value`"""


class LitValue(Value):
    def __init__(self, val: str | int | float | bool) -> None:
        super().__init__()
        self._val = val

    def __repr__(self) -> str:
        return repr(self._val)


################################
# Transformations
################################


class Transformation(DecisionEntity, abc.ABC):
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def on(self, value: IntoValue) -> Transformed:
        pass


class Transformed(Value):
    def __init__(self, opcode: str, *args, **kwargs) -> None:
        super().__init__()
        self.opcode = opcode
        self.args = args
        self.kwargs = kwargs

    def _ar(self, *args, **kwargs) -> str:
        return super()._ar(*self.args, *args, **self.kwargs, **kwargs)

    def __repr__(self) -> str:
        return f"{self.opcode}({self._ar()})"


class TransformSingleNoParam(Transformation):
    def __init__(self, opcode: str) -> None:
        super().__init__()
        self.opcode = opcode

    def on(self, value: IntoValue) -> Transformed:
        return Transformed(self.opcode, value)

    def __call__(self, value: IntoValue) -> Transformed:
        return self.on(value)


to_upper = TransformSingleNoParam("to_upper")
""":class:`Transformation` converting a value to uppercase"""

to_lower = TransformSingleNoParam("to_lower")
""":class:`Transformation` converting a value to lowercase"""

trim = TransformSingleNoParam("trim")
""":class:`Transformation` removing all whitespace from start and end of the stringified value"""

trim_start = TransformSingleNoParam("trim_start")
""":class:`Transformation` removing all whitespace from the start of the stringified value"""

trim_end = TransformSingleNoParam("trim_end")
""":class:`Transformation` removing all whitespace from the end of the stringified value"""


def concat(*clauses: IntoValue) -> Transformed:
    return Transformed("concat", *[Value.of(c) for c in clauses])


def _concat_from_template(temp: templatelib.Template) -> Transformed:
    return concat(
        *tuple(
            x
            for pair in itertools.zip_longest(temp.strings, temp.values)
            for x in pair
            if not (isinstance(x, str) and x == "")
        )[:-1]
    )


################################
# Criteria
################################


class Criterion(DecisionEntity):
    def __init__(self, *, sample_expected: IntoTextValue | None) -> None:
        super().__init__()
        self.sample_expected = Value.of(sample_expected)

    def __bool__(self) -> NoReturn:
        raise TypeError(NO_BOOL_ON_CRITERION + f" ({self!r})")

    def negate(self) -> negated:
        """Create criterion with the success condition negated"""
        return negated(self)

    @property
    def negated(self) -> negated:
        """Criterion with the success condition negated"""
        return negated(self)

    def with_sample_expected(self, val: IntoTextValue) -> Criterion:
        self.sample_expected = Value.of(val)
        return self

    def _ar(self, *args, **kwargs) -> str:
        extend = {}
        if self.sample_expected is not None:
            extend.update(sample_expected=self.sample_expected)
        return super()._ar(*args, **kwargs, **extend)


class compare(Criterion):
    def __init__(
        self,
        left: IntoValue,
        relation: RelationT,
        right: IntoValue,
        *,
        sample_expected: IntoTextValue | None = None,
    ) -> None:
        """
        Compare two future values with a given relation

        :param Value left: first future value
        :param RelationT relation: the comparison relation to use
        :param Value right: second future value
        """
        super().__init__(sample_expected=sample_expected)
        self.left = Value.of(left)
        self.relation = relation
        self.right = Value.of(right)

    def __repr__(self) -> str:
        return f"{self.left!r} {self.relation} {self.right!r}"

    @classmethod
    def eq(cls, left: IntoValue, right: IntoValue) -> compare:
        return cls(left, "==", right)

    @classmethod
    def neq(cls, left: IntoValue, right: IntoValue) -> compare:
        return cls(left, "!=", right)

    @classmethod
    def lt(cls, left: IntoValue, right: IntoValue) -> compare:
        return cls(left, "<", right)

    @classmethod
    def gt(cls, left: IntoValue, right: IntoValue) -> compare:
        return cls(left, ">", right)

    @classmethod
    def le(cls, left: IntoValue, right: IntoValue) -> compare:
        return cls(left, "<=", right)

    @classmethod
    def ge(cls, left: IntoValue, right: IntoValue) -> compare:
        return cls(left, ">=", right)


class Contained(Criterion):
    def __init__(
        self,
        *,
        sub: IntoValue,
        sup: IntoTextValue,
        mode: ContainOpcodeT = "contain_text",
        sample_expected: IntoTextValue | None = None,
    ) -> None:
        super().__init__(sample_expected=sample_expected)
        self.sub = sub
        self.sup = sup
        self.mode = mode

    def __repr__(self) -> str:
        if self.mode == "contain_text":
            return f"{self.sup!r}.contains_text({self._ar(self.sub)})"
        if self.mode == "contain_num":
            return f"{self.sup!r}.contains_this_number({self._ar(self.sub)})"
        if self.mode == "contain_onlynum":
            return f"{self.sup!r}.contains_only_this_number({self._ar(self.sub)})"
        raise TypeError(f"Unexpected contain mode: {self.mode}")


################################
# Criterion junctors
################################


class negated(Criterion):
    def __init__(
        self, inner: Criterion, sample_expected: IntoTextValue | None = None
    ) -> None:
        super().__init__(sample_expected=sample_expected)
        self._inner = inner

    def __repr__(self) -> str:
        return self._repr(self._inner)

    pass


class all_of(Criterion):
    def __init__(
        self, *clauses: Criterion, sample_expected: IntoTextValue | None = None
    ) -> None:
        super().__init__(sample_expected=sample_expected)
        self._clauses = []
        for c in clauses:
            if isinstance(c, self.__class__):
                self._clauses.extend(c._clauses)
            else:
                self._clauses.append(c)

    def __repr__(self) -> str:
        return self._repr(*self._clauses)

    pass


class any_of(Criterion):
    def __init__(
        self, *clauses: Criterion, sample_expected: IntoTextValue | None = None
    ) -> None:
        super().__init__(sample_expected=sample_expected)
        self._clauses = []
        for c in clauses:
            if isinstance(c, self.__class__):
                self._clauses.extend(c._clauses)
            else:
                self._clauses.append(c)

    def __repr__(self) -> str:
        return self._repr(*self._clauses)

    pass


################################
# Selectors
################################


class Selector(Value):
    def __init__(self, opcode: SelectorOpcodeT, *args) -> None:
        super().__init__()
        self._opcode = opcode
        self._args = args


class FutureVariable(Selector):
    def __init__(self, name: str) -> None:
        super().__init__("var", name)

    @property
    def name(self):
        return self._args[0]

    def __repr__(self) -> str:
        return f"VAR({self.name!r})"


class FutureProperty(Selector):
    # As soon as there are more future properties
    # @typing.overload
    # def __init__(
    #     self, *, mode: Literal["array"], group: FutureArray, name: str
    # ) -> None: ...

    def __init__(self, *, mode: Literal["array"], group, name: str) -> None:
        super().__init__(mode + "prop", group, name)
        self._mode = mode

    @property
    def group(self):
        return self._args[0]

    @property
    def name(self):
        return self._args[1]

    def __repr__(self) -> str:
        if self._mode == "array" and self.name == "length":
            return f"{self.group!r}.length"
        raise ValueError(
            f"FutureProperty selector called with unsupported arguments: {self._mode} {self.group} {self.name}"
        )


# TODO: think if key should be allowed to be numeric `Value`
class FutureItem(Selector):
    def __init__(self, array: FutureArray, key: int) -> None:
        super().__init__("arrayitem", array, key)

    @property
    def array(self) -> FutureArray:
        return self._args[0]

    @property
    def position(self) -> int:
        return self._args[1]

    def __repr__(self) -> str:
        return f"{self.array!r}[{self.position}]"


class FutureArray:
    """
    A :class:`FutureArray` represents a specific source of multiple
    values that are available – somewhere in the future – during the
    evaluation of a submission.

    Examples are:
        - :any:`INPUT`: access the input a submission got in the current test
        - :any:`OUTPUT`: access the output a submission produced
        - :any:`LIST(name) <LIST>`: access the list with the provided name

    This type can be used similarily to a list of :class:`Selector`'s:

    >>> first_input = INPUT.first # or INPUT[0]
    >>> first_input
    INPUT[0]
    >>> last_output = OUTPUT.last # or OUTPUT[-1]
    >>> last_output
    OUTPUT[-1]
    >>> mylist = LIST("mylist")
    >>> second_item = mylist[1] # or mylist.index1(2)
    >>> second_item
    LIST("mylist")[1]
    >>> length_of_mylist = mylist.length # don't use len(mylist)
    >>> length_of_mylist
    LIST("mylist").length

    .. attention::

        The values you receive are special instances of :class:`Selector`
        and can be understood as placeholders.
        For more see :ref:`placeholders-in-future`.
    """

    def __init__(self, kind: ArrayScopeT, name: str) -> None:
        super().__init__()
        self._kind: ArrayScopeT = kind
        self._name: str = name

    @property
    def kind(self) -> ArrayScopeT:
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
        return FutureProperty(mode="array", group=self, name="length")

    @property
    def first(self) -> FutureItem:
        return self[0]

    def from_start1(self, onebased_n: int) -> FutureItem:
        assert onebased_n > 0, f"{onebased_n=} should be at least 1"
        return self[onebased_n - 1]

    def from_end1(self, onebased_n: int) -> FutureItem:
        assert onebased_n > 0, f"{onebased_n=} should be at least 1"
        return self[-onebased_n]

    def index1(self, onebased_n: int) -> FutureItem:
        assert onebased_n != 0, (
            "FutureArray: index1(1) means first element, index1(-1) last, but index1(0) is undefined"
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
""":class:`FutureArray` that represents the output a submission produced during the current test"""

INPUT = FutureArray("io", "input")
""":class:`FutureArray` that represents the output a submission got during the current test"""


def LIST(name: str) -> FutureArray:
    return FutureArray("list", name)


def VAR(name: str) -> FutureVariable:
    return FutureVariable(name)
