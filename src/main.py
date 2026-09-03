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
    OUTPUT,
)

c1 = INPUT[0].contains_only_this_number(4)
c2 = OUTPUT[0].contains_text(INPUT[0])

all1 = all_of(c1, c2)
print(c1, c2, all1.with_sample_expected("Sample"))
b = "b"
print(
    Value.of(t"a {INPUT.length} "),
)
print((INPUT.length == "b").with_sample_expected("Hell"))

l = to_lower(INPUT[0])
print(l)

print(Value.of(2) + INPUT[0])
