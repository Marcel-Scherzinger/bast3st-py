from bast3st import OUTPUT, Bast3StSpec, any_of, send_info, INPUT, if_then_else
from bast3st.catchable import err
from bast3st.decisions import Value

spec = Bast3StSpec("Prüfung ob das Produkt zweier Zahlen größer als 50 ist")
spec.set_block_count_limit(30)

category_eq = spec.new_category("Das Produkt der beiden Zahlen ist 50")
category_gt = spec.new_category("Das Produkt der beiden Zahlen ist größer als 50")
category_lt = spec.new_category("Das Produkt der beiden Zahlen ist kleiner als 50")


criterion_gt = OUTPUT.last.contains_text(
    "größer als",
    failure_explaination="Sie hätten etwas ausgeben sollen wie 'Das Produkt der beiden Zahlen ist größer als 50'",
)
criterion_eq = any_of(
    OUTPUT.last.contains_text("nicht größer als"),
    OUTPUT.last.contains_text("gleich").catch(err.network, fallback=(Value.of(1) == 1)),
    failure_explaination="Sie hätten etwas ausgeben sollen wie 'Das Produkt der beiden Zahlen ist nicht größer als 50'",
)
criterion_lt = any_of(
    OUTPUT.last.contains_text("nicht größer als"),
    OUTPUT.last.contains_text("kleiner als"),
    failure_explaination="Sie hätten etwas ausgeben sollen wie 'Das Produkt der beiden Zahlen ist nicht größer als 50'",
)

# this combines all of the above and selects the right one depending on inputs
universal_crit = if_then_else(
    INPUT[0] * INPUT[1] > 50,
    criterion_gt,
    if_then_else(INPUT[0] * INPUT[1] < 50, criterion_lt, criterion_eq),
)

for first in range(-20, 20):
    for second in range(-20, 20):
        product = first * second

        if product == 50:
            case = category_eq.new_test(
                f"{first} * {second} = {product} ?>? 50",
                input=[first, second],
                criterion=criterion_eq,
            ).if_criterion_then(
                OUTPUT.last.contains_text("gleich"),
                send_info(
                    "Ich finde es sehr schön, dass Sie auch Gleichheit unterscheiden"
                ),
            )
        if product < 50:
            case = category_lt.new_test(
                f"{first} * {second} = {product} ?>? 50",
                input=[first, second],
                criterion=criterion_lt,
            )
        if product > 50:
            case = category_gt.new_test(
                f"{first} * {second} = {product} ?>? 50",
                input=[first, second],
                criterion=criterion_gt,
            )

print(spec._node_dict())
with open("examples/compare-with-catch.json", "w", encoding="utf8") as f:
    f.write(spec.to_json(indent=2))
