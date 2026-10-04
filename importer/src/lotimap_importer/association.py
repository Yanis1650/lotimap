"""Attach DXF number texts to the lots that contain them."""

from __future__ import annotations

from collections import Counter

from .models import Issue, Lot, NumberText


def attach_numbers(
    lots: list[Lot], numbers: list[NumberText], issues: list[Issue]
) -> None:
    counts = Counter(number.value for number in numbers)
    for value, count in counts.items():
        if count > 1:
            issues.append(
                Issue("duplicate_number", f"Numéro {value!r} présent {count} fois.")
            )

    for number in numbers:
        containing = [lot for lot in lots if lot.polygon.covers(number.point)]
        if not containing:
            issues.append(
                Issue(
                    "text_outside_lot",
                    f"Texte {number.value!r} hors des lots valides.",
                    layer=number.layer,
                    handle=number.handle,
                )
            )
        elif len(containing) > 1:
            issues.append(
                Issue(
                    "ambiguous_number",
                    f"Texte {number.value!r} dans plusieurs lots.",
                    layer=number.layer,
                    handle=number.handle,
                )
            )
        else:
            containing[0].numbers.append(number)

    for lot in lots:
        if not lot.numbers:
            issues.append(
                Issue(
                    "lot_without_number",
                    "Lot sans numéro rattaché.",
                    layer=lot.layer,
                    handle=lot.handle,
                )
            )
        elif len(lot.numbers) > 1:
            issues.append(
                Issue(
                    "multiple_numbers",
                    "Plusieurs textes rattachés au même lot.",
                    layer=lot.layer,
                    handle=lot.handle,
                )
            )
