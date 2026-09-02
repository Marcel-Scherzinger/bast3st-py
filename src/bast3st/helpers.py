from typing import Literal, Union

Atomic = Union[int, str, float, bool]

ArrayScope = Literal["io", "list"]
RelationT = Literal["==", "!=", "<=", ">=", "<", ">"]
