from typing import Literal, Union

Atomic = Union[int, str, float, bool]

ArrayScopeT = Literal["io", "list"]
RelationT = Literal["==", "!=", "<=", ">=", "<", ">"]
SelectorOpcodeT = Literal["var", "arrayitem", "arrayprop"]
