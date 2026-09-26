from bast3st import Bast3StSpec, OUTPUT
from bast3st.actions import set_flag
from bast3st.decisions import FLAGS, INPUT, PARAM


spec = Bast3StSpec(
    "Ausgabe des Doppelten der Summe der Quadrate von der ersten bis zur zweiten Engabe"
)
spec.set_block_count_limit(30, "Sie verwenden zu viele Blöcke")


def corr(a, b):
    return sum([2 * i * i for i in range(a, b + 1)])


def criterion(a, b):
    return OUTPUT.last.contains_only_this_number(corr(a, b)).with_failure_explaination(
        t"Die korrekte Summe ist {corr(a, b)}"
    )


cat = spec.new_category("1 bis 5, 6 bis 10")
cat.new_test("1 bis 5", criterion=criterion(1, 5), input=[1, 5])
print(
    cat.new_test("6 bis 10", criterion=criterion(6, 10), input=[6, 10])
    .run_action(set_flag("params", "1", value=PARAM.doc("blockcount", "total")))
    .run_action(set_flag("params", "2", value="123"))
    .run_action(
        set_flag(
            "params",
            "3",
            value=PARAM.doc("blockcount", "opcode", "event_whenflagclicked"),
        )
    )
    .run_action(set_flag("params1", value=FLAGS["params"].sum()))
)
print(spec)

with open("examples/dyn_loop.json", "w", encoding="utf8") as f:
    f.write(spec.to_json(indent=2))
