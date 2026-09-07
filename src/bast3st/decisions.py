from __future__ import annotations

from typing import NoReturn, Literal
import abc
from string import templatelib
import itertools
import typing

from bast3st.catchable import err

type StdArrayScopeT = Literal["ior", "list"]
type ArrayScopeT = Literal["arrayview"] | StdArrayScopeT
type MapScopeT = Literal["network", "first_capture", "data", "mapitem", "view"]
type RelationT = Literal["==", "!=", "<=", ">=", "<", ">"]
"""A comparison operator string to specify the desired relation"""

type SelectorOpcodeT = Literal["var", "arrayitem", "arrayprop", "mapitem", "mapprop"]
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
        fmt_kwargs = [f"{k}={v!r}" for (k, v) in kwargs.items() if v is not None]
        fmt_kwargs.sort()
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

    def __add__(self, other: IntoValue, /) -> Value:
        return SerVal("add", self, Value.ofStrict(other))

    def __sub__(self, other: IntoValue, /) -> Value:
        return SerVal("sub", self, Value.ofStrict(other))

    def __mul__(self, other: IntoValue, /) -> Value:
        return SerVal("mul", self, Value.ofStrict(other))

    def __truediv__(self, other: IntoValue, /) -> Value:
        return SerVal("truediv", self, Value.ofStrict(other))

    def __floordiv__(self, other: IntoValue, /) -> Value:
        # // operator (integer division)
        return SerVal("floordiv", self, Value.ofStrict(other))

    def __mod__(self, other: IntoValue, /) -> Value:
        return SerVal("mod", self, Value.ofStrict(other))

    def __pow__(self, other: IntoValue, /) -> Value:
        return SerVal("pow", self, Value.ofStrict(other))

    def __neg__(self, /) -> Value:
        return SerVal("neg", self)

    def __floor__(self, /) -> Value:
        return SerVal("floor", self)

    def __ceil__(self, /) -> Value:
        return SerVal("ceil", self)

    def __round__(self, /) -> Value:
        return SerVal("round", self)

    def __abs__(self, /) -> Value:
        return SerVal("abs", self)

    def contains_text(
        self, val: IntoTextValue, *, failure_explaination: IntoTextValue | None = None
    ) -> Criterion:
        return Contained(
            sub=val,
            sup=self,
            mode="contain_text",
            failure_explaination=failure_explaination,
        )

    def contains_only_this_number(
        self, val: IntoValue, *, failure_explaination: IntoTextValue | None = None
    ) -> Criterion:
        return Contained(
            sub=val,
            sup=self,
            mode="contain_onlynum",
            failure_explaination=failure_explaination,
        )

    def contains_with_gaps(
        self, *val: IntoValue, failure_explaination: IntoTextValue | None = None
    ) -> Criterion:
        """If this contains a specific sequence of fragments, with arbitraty gaps inbetween"""
        return SerCrit(
            "contain_wgap",
            *val,
            sup=self,
            failure_explaination=failure_explaination,
        )

    def matches(
        self, pattern: IntoTextValue, failure_explaination: IntoTextValue | None = None
    ) -> Criterion:
        """
        If this matches a *Rust regex* regular expression.

        .. warning::

            As :ref:`placeholders-in-future` the pattern will be evaluated **not** by the
            Python :mod:`re` regular expression library, but by the one that is used
            by the server implementation.
            The required syntax can be found in the
            `regex crate <https://docs.rs/regex/latest/regex/#syntax>`_

        """
        return SerCrit(
            "regex",
            pattern=pattern,
            sup=self,
            failure_explaination=failure_explaination,
        )

    def first_capture(self, pattern: IntoTextValue) -> FutureMapping:
        """
        Tries to match a *Rust regex* regular expression and returns
        a mapping of the first match that allows accessing the
        `captured parts <https://docs.rs/regex/latest/regex/#grouping-and-flags>`_.

        .. warning::

            As :ref:`placeholders-in-future` the pattern will be evaluated **not** by the
            Python :mod:`re` regular expression library, but by the one that is used
            by the server implementation.
            The required syntax can be found in the
            `regex crate <https://docs.rs/regex/latest/regex/#syntax>`_

        """
        return FirstPatternCapture(pattern, self)

    def contains_this_number(
        self, val: IntoValue, *, failure_explaination: IntoTextValue | None = None
    ) -> Criterion:
        return Contained(
            sub=val,
            sup=self,
            mode="contain_num",
            failure_explaination=failure_explaination,
        )

    def text_is_contained_in(
        self, val: IntoTextValue, *, failure_explaination: IntoTextValue | None = None
    ) -> Criterion:
        return Contained(
            sub=self,
            sup=val,
            mode="contain_text",
            failure_explaination=failure_explaination,
        )

    def pipe(self, *operations: Transformation) -> Value:
        """
        Execute a sequence of transformations in order on this value
        and return the final result. The value itself is the input to
        the first :class:`Transformation` and every further
        :class:`Transformation` gets the output of the last as input.
        The last :class:`Transformation`'s output will be returned.
        """
        val = self
        for op in operations:
            val = op.on(val)
        return val

    def to_upper(self) -> Value:
        return self.pipe(to_upper)

    def to_lower(self) -> Value:
        return self.pipe(to_lower)

    def trim_start(self) -> Value:
        return self.pipe(trim_start)

    def trim_end(self) -> Value:
        return self.pipe(trim_end)

    def trim(self) -> Value:
        return self.pipe(trim)

    @typing.overload
    def catch(
        self,
        error: err,
        *,
        default_value: IntoValue,
        only_if: Criterion | None = None,
    ): ...
    @typing.overload
    def catch(
        self,
        error: err,
        *,
        action: ValueCatchAction,
        only_if: Criterion | None = None,
    ): ...
    @typing.overload
    def catch(
        self,
        error: err,
        *,
        only_if: Criterion | None = None,
        default_value: IntoValue | None,
        action: ValueCatchAction | None,
    ): ...

    def catch(
        self,
        error: err,
        *,
        only_if: Criterion | None = None,
        default_value: IntoValue | None = None,
        action: ValueCatchAction | None = None,
    ) -> Value:
        return SerVal(
            "catch",
            self,
            error,
            only_if=only_if,
            default_value=Value.of(default_value),
            action=action,
        )._with_syntax("meth")


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
# Actions
################################

MsgSeverityT = Literal["info", "warning", "error"]

LevelT_value_catch = Literal["value-catch"]
LevelT_criterion_catch = Literal["criterion-catch"]
ActionScope = typing.TypeVar("ActionScope", LevelT_value_catch, LevelT_criterion_catch)
type LevelT = LevelT_criterion_catch | LevelT_value_catch


class Action(typing.Generic[ActionScope]):
    pass


type ValueCatchAction = Action[LevelT_value_catch]
type CriterionCatchAction = Action[LevelT_criterion_catch]

################################
# Transformations
################################


class Transformation(DecisionEntity, abc.ABC):
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def on(self, value: IntoValue) -> Value:
        pass


class SerVal(Value):
    def __init__(self, opcode: str, *args, **kwargs) -> None:
        super().__init__()
        self.opcode = opcode
        self.args = args
        self.kwargs = kwargs
        self._syntax = "func"

    def _ar(self, *args, **kwargs) -> str:
        return super()._ar(*self.args, *args, **self.kwargs, **kwargs)

    def __repr__(self) -> str:
        if self._syntax == "meth":
            return f"{self.args[0]!r}.{self.opcode}({super()._ar(*self.args[1:], **self.kwargs)})"
        if self._syntax == "prop":
            extra = super()._ar(*self.args[1:], **self.kwargs)
            if len(extra) > 0:
                return f"{self.args[0]!r}.{self.opcode}({extra})"
            else:
                return f"{self.args[0]!r}.{self.opcode}"
        return f"{self.opcode}({self._ar()})"

    def _with_syntax(self, syntax: typing.Literal["func", "meth", "prop"]) -> SerVal:
        self._syntax = syntax
        return self


class TransformSingleNoParam(Transformation):
    def __init__(self, opcode: str) -> None:
        super().__init__()
        self.opcode = opcode

    def on(self, value: IntoValue) -> Value:
        return SerVal(self.opcode, value)

    def __call__(self, value: IntoValue) -> Value:
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


def concat(*clauses: IntoValue) -> Value:
    return SerVal("concat", *[Value.of(c) for c in clauses])


def _concat_from_template(temp: templatelib.Template) -> Value:
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
    def __init__(self, *, failure_explaination: IntoTextValue | None) -> None:
        super().__init__()
        self.failure_explaination = Value.of(failure_explaination)

    def __bool__(self) -> NoReturn:
        raise TypeError(NO_BOOL_ON_CRITERION + f" ({self!r})")

    def negate(self, *, failure_explaination: IntoTextValue | None = None) -> Criterion:
        """Create criterion with the success condition negated"""
        return negated(self, failure_explaination=failure_explaination)

    @property
    def negated(self) -> Criterion:
        """Criterion with the success condition negated"""
        return negated(self)

    def with_failure_explaination(self, val: IntoTextValue) -> Criterion:
        self.failure_explaination = Value.of(val)
        return self

    def _ar(self, *args, **kwargs) -> str:
        extend = {}
        if self.failure_explaination is not None:
            extend.update(failure_explaination=self.failure_explaination)
        return super()._ar(*args, **kwargs, **extend)

    @typing.overload
    def catch(
        self,
        error: err,
        *,
        fallback: Criterion,
        only_if: Criterion | None = None,
    ): ...
    @typing.overload
    def catch(
        self,
        error: err,
        *,
        action: CriterionCatchAction,
        only_if: Criterion | None = None,
    ): ...
    @typing.overload
    def catch(
        self,
        error: err,
        *,
        only_if: Criterion | None = None,
        fallback: Criterion | None,
        action: CriterionCatchAction | None,
    ): ...

    def catch(
        self,
        error: err,
        *,
        only_if: Criterion | None = None,
        fallback: Criterion | None = None,
        action: CriterionCatchAction | None = None,
    ) -> Criterion:
        return SerCrit(
            "catch",
            error,
            only_if=only_if,
            fallback=fallback,
            action=action,
        )


class SerCrit(Criterion):
    def __init__(
        self,
        opcode: str,
        *args,
        failure_explaination: IntoTextValue | None = None,
        **kwargs,
    ) -> None:
        super().__init__(failure_explaination=Value.of(failure_explaination))
        self._consname = self.__class__.__name__
        self.opcode = opcode
        self._args = args
        self._kwargs = kwargs

    def _ar(self, *args, **kwargs) -> str:
        return super()._ar(
            *self._args,
            *args,
            **self._kwargs,
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"{self._consname}({self._ar()})"


@typing.overload
def if_then_else(if_: Criterion, then_: Criterion, else_: Criterion) -> Criterion: ...
@typing.overload
def if_then_else(if_: Criterion, then_: IntoValue, else_: IntoValue) -> Value: ...


def if_then_else(if_, then_, else_):  # type: ignore
    if isinstance(then_, Criterion):
        if isinstance(else_, Criterion):
            return SerCrit("ifte", if_, then_, else_)
    else:
        if not isinstance(else_, Criterion):
            return SerVal("ifte", if_, then_, else_)

    raise TypeError("Can't use if_then_else with mixed signature for then_/else_")


class compare(SerCrit):
    def __init__(
        self,
        left: IntoValue,
        relation: RelationT,
        right: IntoValue,
        *,
        failure_explaination: IntoTextValue | None = None,
    ) -> None:
        """
        Compare two future values with a given relation

        :param Value left: first future value
        :param RelationT relation: the comparison relation to use
        :param Value right: second future value
        """
        super().__init__(
            relation,
            Value.of(left),
            Value.of(right),
            failure_explaination=failure_explaination,
        )

    @property
    def relation(self):
        return self.opcode

    @property
    def left(self) -> Value:
        return self._args[0]

    @property
    def right(self) -> Value:
        return self._args[1]

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


class Contained(SerCrit):
    def __init__(
        self,
        *,
        sub: IntoValue,
        sup: IntoTextValue,
        mode: ContainOpcodeT = "contain_text",
        failure_explaination: IntoTextValue | None = None,
    ) -> None:
        super().__init__(
            mode,
            Value.of(sub),
            Value.of(sup),
            failure_explaination=failure_explaination,
        )

    @property
    def mode(self) -> ContainOpcodeT:
        return self.opcode  # type: ignore

    @property
    def sub(self) -> Value:
        return self._args[0]

    @property
    def sup(self) -> Value:
        return self._args[1]

    def __repr__(self) -> str:
        kw = (
            f", failure_explaination={self.failure_explaination!r}"
            if self.failure_explaination is not None
            else ""
        )
        if self.mode == "contain_text":
            return f"{self.sup!r}.contains_text({self._ar(self.sub)}{kw})"
        if self.mode == "contain_num":
            return f"{self.sup!r}.contains_this_number({self._ar(self.sub)}{kw})"
        if self.mode == "contain_onlynum":
            return f"{self.sup!r}.contains_only_this_number({self._ar(self.sub)}{kw})"
        raise TypeError(f"Unexpected contain mode: {self.mode}")


################################
# Criterion junctors
################################


def negated(
    criterion: Criterion, *, failure_explaination: IntoTextValue | None = None
) -> Criterion:
    """Negate a criterion so that it accepts exactly when the original one didn't accept"""
    c = SerCrit("negated", criterion, failure_explaination=failure_explaination)
    c._consname = "negated"
    return c


class all_of(SerCrit):
    def __init__(
        self, *clauses: Criterion, failure_explaination: IntoTextValue | None = None
    ) -> None:
        _clauses = []
        for c in clauses:
            if isinstance(c, self.__class__):
                _clauses.extend(c._args)
            else:
                _clauses.append(c)

        super().__init__(
            self.__class__.__name__,
            *_clauses,
            failure_explaination=failure_explaination,
        )

    pass


class any_of(SerCrit):
    def __init__(
        self, *clauses: Criterion, failure_explaination: IntoTextValue | None = None
    ) -> None:
        _clauses = []
        for c in clauses:
            if isinstance(c, self.__class__):
                _clauses.extend(c._args)
            else:
                _clauses.append(c)

        super().__init__(
            self.__class__.__name__,
            *_clauses,
            failure_explaination=failure_explaination,
        )


################################
# Selectors
################################


class Selector(Value):
    def __init__(self, opcode: SelectorOpcodeT, *args) -> None:
        Value.__init__(self)
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


class FutureArray(typing.Protocol):
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


    (This type should not be instantiated directly)
    """

    def __getitem__(self, key: int) -> Value: ...
    @property
    def last(self) -> Value: ...
    @property
    def length(self) -> Value: ...
    @property
    def first(self) -> Value: ...
    def from_start1(self, onebased_n: int) -> Value: ...
    def from_end1(self, onebased_n: int) -> Value: ...
    def index1(self, onebased_n: int) -> Value: ...


def LIST(name: str) -> FutureArray:
    return DATA["lists", name]


def VAR(name: str) -> FutureVariable:
    return DATA["variables", name]  # type: ignore


class FutureMapping(DecisionEntity):
    """
    This is a key-value-mapping that lives in the future. (See :class:`FutureArray`)
    """

    def __init__(self, kind: MapScopeT, *args, **kwargs) -> None:
        super().__init__()
        self._kind: MapScopeT = kind
        self._args = args
        self._kwargs = kwargs
        self._definitly_array = False

    @property
    def kind(self) -> MapScopeT:
        return self._kind

    def __getitem__(
        self, key: IntoValue | list[IntoValue] | tuple[IntoValue, ...]
    ) -> FutureMapItem:
        """
        Get the item with the specified key.

        If the provided key is a sequence (tuple/list) of atomic key values,
        this is interpreted as accessing multiple nesting levels deep.
        This is important for JSON-like structures with multiple levels.
        """
        return FutureMapItem(self, key)

    @property
    def length(self) -> Value:
        """The number of items in the mapping"""
        return SerVal("length", self)._with_syntax("prop")

    def keys(self) -> FutureArray:
        """Array of all keys of the mapping (indexed by numbers), in their sorting order"""
        return FutureViewMapping("view", "keys", self)

    def values(self) -> FutureArray:
        """Array of all values of the mapping (indexed by numbers), in the order of the sorted keys"""
        return FutureViewMapping("view", "values", self)

    @property
    def last(self) -> Value:
        """
        On arrays this will return the last element (length-1),
        but on mappings this will be the element with the biggest key (sort order)
        """
        if self._definitly_array:
            return self[-1]
        return self.values()[-1]

    @property
    def first(self) -> Value:
        """
        On arrays this will return the first element (index 0),
        but on mappings this will be the element with the smallest key (sort order)
        """
        if self._definitly_array:
            return self[0]
        return self.values()[0]

    def from_start1(self, onebased_n: int) -> Value:
        assert onebased_n > 0, f"{onebased_n=} should be at least 1"
        return self[onebased_n - 1]

    def from_end1(self, onebased_n: int) -> Value:
        assert onebased_n > 0, f"{onebased_n=} should be at least 1"
        return self[-onebased_n]

    def index1(self, onebased_n: int) -> Value:
        assert onebased_n != 0, (
            "index1(1) means first element, index1(-1) last, but index1(0) is undefined"
        )
        if onebased_n > 0:
            return self[onebased_n - 1]
        return self[-onebased_n]

    def __repr__(self) -> str:
        return super()._repr(*self._args, **self._kwargs)

    def _format_item_repr(self, key: tuple[Value, ...], base: str | None = None) -> str:
        keys = "".join([f"[{k!r}]" for k in key])
        base = base if base is not None else repr(self)
        return f"{base}{keys}"


class FutureMapItem(Selector, FutureMapping):
    def __init__(
        self,
        mapping: FutureMapping,
        key: IntoValue | tuple[IntoValue, ...] | list[IntoValue],
    ) -> None:
        if not isinstance(key, tuple) and not isinstance(key, list):
            key = (key,)
        if isinstance(mapping, FutureMapItem):
            key = (*mapping._my_key, *key)
            mapping = mapping.mapping
        key = tuple([Value.of(k) for k in key])
        # set both constructors to the same *args as both of them
        # set self._args. Thisway we know exactly what self._args will be
        FutureMapping.__init__(self, "mapitem", mapping, key)
        Selector.__init__(self, "mapitem", mapping, key)

    @property
    def mapping(self) -> FutureMapping:
        return self._args[0]

    @property
    def _my_key(self) -> tuple[Value, ...]:
        return self._args[1]

    def __repr__(self) -> str:
        return self.mapping._format_item_repr(self._my_key)


class FutureViewMapping(FutureMapping):
    @property
    def perspective(self):
        """The thing this view makes accessible"""
        return self._args[0]

    @property
    def inner_viewed(self):
        return self._args[1]

    def __init__(
        self,
        kind: Literal["view"],
        perspective: Literal["keys", "values"],
        mapping: FutureMapping,
        /,
    ) -> None:
        super().__init__(kind, perspective, mapping)

    def __repr__(self) -> str:
        return f"{self.inner_viewed!r}.{self.perspective}()"

    pass


class FirstPatternCapture(FutureMapping):
    def __init__(self, pattern: IntoTextValue, value: Value) -> None:
        super().__init__("first_capture", pattern, value)

    def __repr__(self) -> str:
        return f"{self._args[1]!r}.first_capture({self._args[0]}!r)"


class NetworkRequest(FutureMapping):
    """
    A network request to a specific server.
    The server's domain has to be a static string and must be explicitly
    whitelisted by the server administrator

    .. todo:: name the error if not whitelisted

    .. todo:: explicit response attribute methods for selecting.

    :param str server: The server to contact
    :param str route: The part after the first slash that specifies the route on the server
    :param method: The `HTTP Method <https://developer.mozilla.org/en/docs/Web/HTTP/Reference/Methods>`_
        to use for the request. Only `GET` and `POST` are supported
    :param json: A :class:`dict` of values that should be sent as json to the specified url.
        The json attribute is **not** available for `GET` requests.
    :param allowed_status: The
        `HTTP status codes <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status>`_
        of the response that are considered normal behaviour of the API.
        This can be a single number or a :class:`tuple` of status codes.
        If the server responds with a code that isn't listed here, it will be considered
        one of the :ref:`catchable-errors`,
        but only if a map item is used that is expected to require a successful response.

    :ref:`catchable-errors`
    -----------------------

    - :any:`err.network_statusDisallowed`
    - :any:`err.network_respInvalid_notJson`
    - :any:`err.network`
    """

    @typing.overload
    def __init__(
        self,
        *,
        server: str,
        route: IntoTextValue,
        method: Literal["GET"],
        allowed_status: int | tuple[int, ...] = 200,
    ) -> None: ...

    @typing.overload
    def __init__(
        self,
        *,
        server: str,
        route: IntoTextValue,
        method: Literal["POST"],
        json: dict[IntoValue, IntoValue] | None = None,
        allowed_status: int | tuple[int, ...] = 200,
    ) -> None: ...

    def __init__(
        self,
        *,
        server: str,
        route: IntoTextValue,
        method: Literal["GET", "POST"],
        json: dict[IntoValue, IntoValue] | None = None,
        allowed_status: int | tuple[int, ...] = 200,
    ) -> None:
        super().__init__(
            "network",
            server=server,
            route=Value.of(route),
            method=method,
            json=json,
            allowed_status=allowed_status,
        )


class _Data(FutureMapping):
    """
    :ref:`catchable-errors`
    -----------------------

    .. todo:: fill
    """

    def __init__(
        self,
    ) -> None:
        super().__init__(
            "data",
        )

    @typing.overload
    def __getitem__(self, key: Literal["variables", "lists"]) -> FutureMapping: ...  # type: ignore
    @typing.overload
    def __getitem__(
        self, key: Literal["output", "input", "randoms"]
    ) -> FutureArray: ...  # type: ignore
    @typing.overload
    def __getitem__(
        self, key: tuple[Literal["variables", "lists"], IntoTextValue]
    ) -> FutureMapping: ...  # type: ignore
    @typing.overload
    def __getitem__(
        self, key: tuple[Literal["output", "input", "randoms"], IntoValue]
    ) -> FutureMapping: ...  # type: ignore
    @typing.overload
    def __getitem__(
        self, key: tuple[Literal["lists"], IntoTextValue, IntoValue]
    ) -> FutureMapping: ...  # type: ignore

    def __getitem__(  # type: ignore
        self, key
    ) -> FutureMapItem:
        return super().__getitem__(key)

    @property
    def variables(self) -> FutureMapping:
        return self["variables"]

    @property
    def lists(self) -> FutureMapping:
        return self["lists"]

    @property
    def input(self) -> FutureArray:
        return self["input"]

    @property
    def output(self) -> FutureArray:
        return self["output"]

    @property
    def randoms(self) -> FutureArray:
        return self["randoms"]

    def _format_item_repr(self, key: tuple[Value, ...], base=None) -> str:
        if (
            len(key) >= 1
            and isinstance(key[0], LitValue)
            and isinstance(top := key[0]._val, str)
        ):
            if len(key) >= 2:
                if top == "lists":
                    return f"LIST({key[1]!r})" + super()._format_item_repr(
                        key[2:], base=""
                    )
                if top == "variables":
                    return f"VAR({key[1]!r})" + super()._format_item_repr(
                        key[2:], base=""
                    )
            if top in ("input", "output", "randoms"):
                return top.upper() + super()._format_item_repr(key[1:], base="")

        return super()._format_item_repr(key, base=base)

    def __repr__(self) -> str:
        return "DATA"


DATA = _Data()


OUTPUT: FutureArray = DATA["output"]
""":class:`FutureArray` that represents the output a submission produced during the current test"""

INPUT: FutureArray = DATA["input"]
""":class:`FutureArray` that represents the output a submission got during the current test"""

RANDOMS: FutureArray = DATA["randoms"]
""":class:`FutureArray` that represents the random numbers a submission requested and got during the current test"""
