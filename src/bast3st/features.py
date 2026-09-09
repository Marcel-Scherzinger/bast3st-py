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


type PermittedFEAT_TestScope = (
    FA_sendmsg_spec
    | FA_sendmsg_category
    | FA_sendmsg_maintest
    | FA_sendmsg_thistest
    | FS_read_rundata
)

# Criterion that decides if a test should be passed
type PermittedFEAT_PassTestCrit = FA_end_this_test | PermittedFEAT_TestScope
# Criterion that decides if a specific action should be triggered for a test
type PermittedFEAT_CondTestActCrit = PermittedFEAT_TestScope
# Action that is triggered for a test
type PermittedFEAT_CondTestActAct = PermittedFEAT_TestScope

# Criterion that decides if a specific action should be triggered for an alternative test
type PermittedFEAT_CondAltTestActCrit = PermittedFEAT_TestScope
# Action that is triggered for an alternative test
type PermittedFEAT_CondAltTestActAct = PermittedFEAT_TestScope


type PermittedFEAT_CategoryScope = FA_sendmsg_spec | FA_sendmsg_category

# Criterion that decides if a specific action should be triggered for a category
type PermittedFEAT_CondCatActCrit = PermittedFEAT_CategoryScope
# Action that is triggered for a category
type PermittedFEAT_CondCatActAct = PermittedFEAT_CategoryScope


type PermittedFEAT_SpecScope = FA_sendmsg_spec | FA_sendmsg_category

# Criterion that decides if a specific action should be triggered for a spec
type PermittedFEAT_CondSpecActCrit = PermittedFEAT_SpecScope
# Action that is triggered for a spec
type PermittedFEAT_CondSpecActAct = PermittedFEAT_SpecScope
