from typing import overload
from .decisions import (
    Action,
    ActionScope,
    LevelT_criterion_catch,
    LevelT_value_catch,
    LevelT,
    MsgSeverityT,
)


class SendMsg(Action[ActionScope]):
    def __init__(self, text: str, level: LevelT | None, severity: MsgSeverityT) -> None:
        super().__init__()
        self.text = text
        self.level = level
        self.severity = severity


@overload
def send_info(text: str, level: None = None) -> Action[ActionScope]: ...
@overload
def send_info(text: str, level: LevelT_value_catch) -> Action[LevelT_value_catch]: ...
@overload
def send_info(
    text: str, level: LevelT_criterion_catch
) -> Action[LevelT_criterion_catch]: ...


def send_info(text: str, level: LevelT | None = None) -> Action[ActionScope]:
    return SendMsg(text=text, level=level, severity="info")
