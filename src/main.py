from bast3st.decisions import (
    all_of,
    any_of,
    negated,
    Criterion,
    concat,
    Value,
    compare,
    to_lower,
    INPUT,
)

c1 = Criterion(sample_expected="abc")
c2 = Criterion()

all1 = all_of(c1, c2)
print(c1, c2, all1)
b = "b"
print(
    Value.of(t"a {INPUT.length} "),
)
print(INPUT.length == "b")

l = to_lower(INPUT[0])
print(l)

print(Value.of(2) + INPUT[0])
