import typing
import json

from bast3st._general import MAX_INLINE_STR_LEN, ForceInline
from bast3st.decisions import LitValue


class DecisionSerializer:
    def __init__(self) -> None:
        self._repr_to_id = {}
        self._last_id = 0
        self._final = {}

    def register(self, entity) -> int | None | typing.Any:
        """Use repr(entity) as key to get a unique id"""
        r = repr(entity)
        if (val := self._repr_to_id.get(r, None)) is not None:
            return val

        if entity is None:
            return None
        elif isinstance(entity, (tuple, list)):
            obj = [self.register(x) for x in entity]
            if len(entity) == 0:
                return None
            return obj

        elif isinstance(entity, (int, float, bool)):
            entity = LitValue(entity)
        elif isinstance(entity, LitValue) and isinstance(entity._val, str):
            entity = entity._val

        if isinstance(entity, str):
            obj = entity
            if len(obj) <= MAX_INLINE_STR_LEN:
                return obj
        else:
            obj = entity._to_json_able(self)
            if isinstance(obj, ForceInline):
                return obj
            if isinstance(obj, dict):
                obj = {k: self.register(v) for (k, v) in obj.items() if v is not None}

        self._last_id += 1
        self._repr_to_id[r] = self._last_id

        self._final[self._last_id] = obj
        return ForceInline(self._last_id)

    def registerDictStar(self, entity: dict | None) -> dict:

        if isinstance(entity, dict):
            return {k: self.register(v) for (k, v) in entity.items()}

        y = self.register(entity)
        if y is None:
            return {}
        return y  # type: ignore

    def __str__(self) -> str:
        return json.dumps(self._final, indent=2)

    def min_json(self) -> str:
        return json.dumps(self._final)


def _ser_post_process(v):
    if isinstance(v, ForceInline):
        return v._val
    return v
