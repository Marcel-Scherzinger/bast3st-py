from typing import Literal, overload
from .decisions import (
    Action,
    SerAct,
    IntoTextValue,
    IntoValue,
    MsgSeverityT,
    Value,
)
from .features import (
    FA_end_this_test,
    FA_sendmsg_category,
    FA_sendmsg_maintest,
    Features,
    Features2,
    Features3,
)


type LevelT = Literal["maintest", "alttest", "thistest", "category", "spec"]


class SendMsg(SerAct[Features]):
    def __init__(
        self,
        text: IntoTextValue[Features],
        level: LevelT | None,
        severity: MsgSeverityT,
    ) -> None:
        super().__init__("send-msg", t=text, l=level, s=severity)
        self.text = Value.of(text)
        self.level = level
        self.severity = severity

    def __repr__(self) -> str:
        return f"send_{self.severity}({Action._ar(self, self.text, level=self.level)})"


@overload
def send_message(
    text: IntoTextValue[Features], severity: MsgSeverityT, level: None = None
) -> Action[Features]: ...
@overload
def send_message(
    text: IntoTextValue[Features], severity: MsgSeverityT, level: Literal["maintest"]
) -> Action[Features | FA_sendmsg_maintest]: ...
@overload
def send_message(
    text: IntoTextValue[Features], severity: MsgSeverityT, level: Literal["category"]
) -> Action[Features | FA_sendmsg_category]: ...


def send_message(
    text: IntoTextValue, severity: MsgSeverityT, level: LevelT | None = None
) -> Action:
    return SendMsg(text=text, level=level, severity=severity)


# INFO


@overload
def send_info(
    text: IntoTextValue[Features], level: None = None
) -> Action[Features]: ...
@overload
def send_info(
    text: IntoTextValue[Features], level: Literal["maintest"]
) -> Action[Features | FA_sendmsg_maintest]: ...
@overload
def send_info(
    text: IntoTextValue[Features], level: Literal["category"]
) -> Action[Features | FA_sendmsg_category]: ...
@overload
def send_info(
    text: IntoTextValue[Features], level: Literal["spec"]
) -> Action[Features]: ...


def send_info(text: IntoTextValue, level: LevelT | None = None) -> Action:
    return SendMsg(text=text, level=level, severity="info")


# WARNING


@overload
def send_warning(
    text: IntoTextValue[Features], level: None = None
) -> Action[Features]: ...
@overload
def send_warning(
    text: IntoTextValue[Features], level: Literal["maintest"]
) -> Action[Features | FA_sendmsg_maintest]: ...
@overload
def send_warning(
    text: IntoTextValue[Features], level: Literal["category"]
) -> Action[Features | FA_sendmsg_category]: ...
@overload
def send_warning(
    text: IntoTextValue[Features], level: Literal["spec"]
) -> Action[Features]: ...


def send_warning(text: IntoTextValue, level: LevelT | None = None) -> Action:
    return SendMsg(text=text, level=level, severity="warning")


# ERROR


@overload
def send_error(
    text: IntoTextValue[Features], level: None = None
) -> Action[Features]: ...
@overload
def send_error(
    text: IntoTextValue[Features], level: Literal["maintest"]
) -> Action[Features | FA_sendmsg_maintest]: ...
@overload
def send_error(
    text: IntoTextValue[Features], level: Literal["category"]
) -> Action[Features | FA_sendmsg_category]: ...
@overload
def send_error(
    text: IntoTextValue[Features], level: Literal["spec"]
) -> Action[Features]: ...


def send_error(text: IntoTextValue, level: LevelT | None = None) -> Action:
    return SendMsg(text=text, level=level, severity="error")


# end test


def pass_this_test_immediatly(
    explaination: IntoTextValue[Features],
) -> Action[Features | FA_end_this_test]:
    return SerAct("end-this-test", m="pass", e=explaination)


def fail_this_test_immediatly(
    explaination: IntoTextValue[Features],
) -> Action[Features | FA_end_this_test]:
    return SerAct("end-this-test", m="fail", e=explaination)


def end_this_test_immediatly(
    explaination: IntoTextValue[Features], *mode: Literal["fail", "pass"]
) -> Action[Features | FA_end_this_test]:
    return SerAct("end-this-test", m=mode, e=explaination)


# set flag


def set_flag(
    first_key: IntoTextValue[Features],
    *other_keys: IntoTextValue[Features2],
    value: IntoValue[Features3],
) -> Action[Features | Features2 | Features3]:
    """
    Set a custom key to a custom value that can be accessed using this key during other stages.

    Note that empty strings take a special position as key-components.
    If you assign a non-mapping value to ("level1", "level2") and then assign
    a value to ("level1", "level2", "newlevel") a new level needs to be created to store the
    second value. The first one will from there on be available as ("level1", "level2", "")
    and no longer as ("level1", "level2") which will be the mapping containing "" and "newlevel".
    But no one stops you from using empty strings as keys, it could just cause weird effects.

    Flags set during the evaluation of one value are typically only available after the completion
    of the entire evaluation i.e. a if a value that executed this action by catching an error
    is used for a value that tries to read this flag, this last set will be invisible.
    See the documentation for detailed flag-visibility rules, you may be surprised.

    Flags form a nested mapping and the test specification is free to specify them
    in a useful hierarchy of levels for structuring communication.

    You have to use at least one key level (you can't set the top-level flags mapping).
    """
    return SerAct(
        "set-flag",
        k=[Value.of(first_key)] + [Value.of(k) for k in other_keys],
        v=Value.of(value),
    )
