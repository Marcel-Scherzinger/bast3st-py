from bast3st import Bast3StSpec, OUTPUT


spec = Bast3StSpec("Ausgabe des Doppelten der Summe der Quadrate von 1 bis 5")
spec.set_block_count_limit(30, "Sie verwenden zu viele Blöcke")


correct = 2 * (1 + 2 * 2 + 3 * 3 + 4 * 4 + 5 * 5)

perfect_output = OUTPUT.last.contains_only_this_number(
    correct
).with_failure_explaination(t"Die korrekte Summe ist {correct}")

cat = spec.new_category("1 bis 5")
cat.new_test("1 bis 5", criterion=perfect_output)
print(spec)

with open("examples/fixed_loop.json", "w", encoding="utf8") as f:
    f.write(spec.to_json(indent=2))
