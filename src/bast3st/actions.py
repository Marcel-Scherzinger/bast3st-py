from typing import Literal, overload
import typing
from .decisions import (
    Action,
    IntoTextValue,
    MsgSeverityT,
    Value,
)
from .features import (
    FA_end_this_test,
    FA_sendmsg_category,
    FA_sendmsg_maintest,
    Features,
)


class SerAct(Action[Features]):
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

    def _with_syntax(self, syntax: typing.Literal["func", "meth", "prop"]) -> SerAct:
        self._syntax = syntax
        return self


type LevelT = Literal["maintest", "alttest", "thistest", "category", "spec"]


class SendMsg(Action[Features]):
    def __init__(
        self,
        text: IntoTextValue[Features],
        level: LevelT | None,
        severity: MsgSeverityT,
    ) -> None:
        super().__init__()
        self.text = Value.of(text)
        self.level = level
        self.severity = severity

    def __repr__(self) -> str:
        return f"send_{self.severity}(text={self.text!r}, level={self.level})"


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
) -> Action[FA_end_this_test]:
    return SerAct("end-this-test", "pass", explaination)


def fail_this_test_immediatly(
    explaination: IntoTextValue[Features],
) -> Action[FA_end_this_test]:
    return SerAct("end-this-test", "fail", explaination)


def end_this_test_immediatly(
    explaination: IntoTextValue[Features], *mode: Literal["fail", "pass"]
) -> Action[FA_end_this_test]:
    return SerAct("end-this-test", mode, explaination)
