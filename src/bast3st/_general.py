MAX_INLINE_STR_LEN = 42


class ForceInline:
    def __init__(self, s) -> None:
        self._val = s

    def __repr__(self) -> str:
        return f"Inline({self._val!r})"

    def _to_json_able(self, ser):
        return self


def kebab_keys(d):
    if isinstance(d, dict):
        return {k.replace("_", "-"): kebab_keys(v) for (k, v) in d.items()}
    return d
