from bast3st import (
    OUTPUT,
    INPUT,
    Bast3StSpec,
)


spec = Bast3StSpec("Begrüßung eines gegebenen Namens")
spec.set_block_count_limit(20, "Sie verwenden zu viele Blöcke")

NAME = INPUT.first

perfect_output = OUTPUT.last.contains_text(NAME).with_failure_explaination(
    t"Wie wäre es mit folgendem: Guten Tag {NAME}"
)


def add_category(title, names: list[str]):
    cat = spec.new_category(title)
    for name in names:
        cat.new_test(f"Begrüße {name}", input=[name], criterion=perfect_output)


# Nur Vornamen oder Namen ohne Leer- und Sonderzeichen
add_category("Vornamen und Namen ohne Sonderzeichen", ["Alan", "Albert"])
