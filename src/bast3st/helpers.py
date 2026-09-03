from typing import Literal, Union

Atomic = Union[int, str, float, bool]

ArrayScopeT = Literal["io", "list"]
RelationT = Literal["==", "!=", "<=", ">=", "<", ">"]
SelectorOpcodeT = Literal["var", "arrayitem", "arrayprop"]
ContainOpcodeT = Literal["contain_onlynum", "contain_num", "contain_text"]
