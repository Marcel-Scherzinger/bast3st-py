from bast3st.actions import send_info, Action
from bast3st.ser import DecisionSerializer
from bast3st.decisions import (
    Criterion,
    any_of,
    INPUT,
    OUTPUT,
    Value,
    all_of,
    to_lower,
    NetworkRequest,
    RANDOMS,
    err,
)
from bast3st.features import FA_sendmsg_maintest, FS_read_rundata
from bast3st.spec import Bast3StSpec

c1 = INPUT[0].contains_only_this_number(4)
c2 = OUTPUT[0].contains_text(INPUT[0])

all1 = all_of(c1, c2)
print(c1, c2)
print(all1.with_failure_explaination("Sample"))
b = "b"
print(
    Value.of(t"a {INPUT.length} "),
)
print((INPUT.length == "b").with_failure_explaination("Hell"))

l = to_lower(INPUT[0])
print(l)

v1 = Value.of(2) + INPUT[0]
c1 = v1.contains_only_this_number("a")
a1 = send_info(v1, level="category")
print(v1)

m = NetworkRequest(server="", route="", method="GET")
print(m["a", "b", 1])
print(repr(err.missingSelection_list_whole))

print(x := m["abc"]["dev"])
print(x[1])

w = Value.of(2).contains_with_gaps(INPUT[0], OUTPUT[0], RANDOMS.length)
x = any_of(w)
print(RANDOMS.length)


act = send_info(text=RANDOMS.length.__add__(INPUT.length), level="maintest")


def test_it(a: Criterion[FA_sendmsg_maintest]):
    print(a)


spec = Bast3StSpec("Aufgabe 3a")

cat1 = spec.new_category("Teilbar durch 2")
spec.if_criterion_then(Value.of("abc").contains_text("a"), send_info("Hallo"))

c2 = (
    OUTPUT.last.to_lower()
    == NetworkRequest(server="", route="", method="POST", json=[(INPUT.length, 2)])[
        0
    ].catch(err.network, default_value=0)
).with_failure_explaination("Die letzte Ausgabe sollte genau die erste Eingabe sein")
test1 = cat1.new_test(
    "Test 1",
    criterion=c2,
)
c1 = OUTPUT.last.contains_text(INPUT.first).with_failure_explaination(
    "Die letzte Ausgabe sollte die erste Eingabe zumindest enthalten"
)

alt1 = test1.new_alternative_test(
    "Alt 1",
    criterion=c1,
)
print(spec)


print(spec.to_json(indent=2))
