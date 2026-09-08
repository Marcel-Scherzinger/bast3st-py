import typing
from typing import Literal

Features = typing.TypeVar("Features", covariant=True)
Features2 = typing.TypeVar("Features2", covariant=True)
Features3 = typing.TypeVar("Features3", covariant=True)
Features4 = typing.TypeVar("Features4", covariant=True)


# Features for Actions
FA_end_this_test = Literal["f-end-this-test"]
FA_sendmsg_spec = Literal["f-sendmsg-spec"]
FA_sendmsg_category = Literal["f-sendmsg-category"]
FA_sendmsg_maintest = Literal["f-sendmsg-maintest"]
FA_sendmsg_thistest = Literal["f-sendmsg-thistest"]

# Features for Selections
FS_read_rundata = Literal["f-read-rundata"]
# FS_read_randoms = Literal["f-read-randoms"]
# FS_read_input = Literal["f-read-input"]
# FS_read_output = Literal["f-read-output"]
