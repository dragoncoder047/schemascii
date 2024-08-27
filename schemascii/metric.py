import re
from decimal import Decimal

METRIC_NUMBER = re.compile(
    r"(\d*\.?\d+)([pnumKkMGT]?)")  # cSpell:ignore pnum
METRIC_RANGE = re.compile(
    r"(\d*\.?\d+[pnumKkMGT]?)-(\d*\.?\d+[pnumKkMGT]?)")
ENG_NUMBER = re.compile(r"^(\d*\.?\d+)[Ee]?([+-]?\d*)$")


def exponent_to_multiplier(exponent: int) -> str | None:
    """Turns the 10-power into a Metric multiplier.

    * 3 --> "k" (kilo)
    * 0 --> ""  (no multiplier)
    * -6 --> "u" (micro)

    If it is not a multiple of 3, returns None.
    """
    if exponent % 3 != 0:
        return None
    index = (exponent // 3) + 4  # pico is -12 --> 0
    # cSpell:ignore pico
    return "pnum kMGT"[index].strip()


def multiplier_to_exponent(multiplier: str) -> int:
    """Turns the Metric multiplier into its exponent.

    * "k" -->  3 (kilo)
    * " " -->  0 (no multiplier)
    * "u" --> -6 (micro)
    """
    if multiplier in (" ", ""):
        return 0
    if multiplier == "µ":
        multiplier = "u"  # allow unicode
    if multiplier == "K":
        multiplier = multiplier.lower()
        # special case (preferred is lowercase)
    i = "pnum kMGT".index(multiplier)
    return (i - 4) * 3


def best_exponent(num: Decimal, six: bool) -> tuple[str, int]:
    """Finds the best exponent for the number.
    Returns a tuple (digits, best_exponent)
    """
    res = ENG_NUMBER.match(num.to_eng_string())
    assert res
    digits, exp = Decimal(res.group(1)), int(res.group(2) or "0")
    assert exp % 3 == 0, "failed to make engineering notation"
    possibilities = []
    for push in range(-12, 9, 3):
        if six and (exp + push) % 6 != 0:
            continue
        new_exp = exp - push
        new_digits = str(digits * (Decimal(10) ** Decimal(push)))
        if "e" in new_digits.lower():
            # we're trying to avoid getting exponential notation here
            continue
        if "." in new_digits:
            new_digits = new_digits.rstrip("0").removesuffix(".")
        possibilities.append((new_digits, new_exp))
    # heuristics:
    #   * shorter is better
    #   * prefer no decimal point
    #   * prefer no Metric multiplier if possible
    return sorted(
        possibilities, key=lambda x: ((10 * len(x[0]))
                                      + (2 * ("." in x[0]))
                                      + (5 * (x[1] != 0))))[0]


def normalize_metric(num: str, six: bool, unicode: bool) -> tuple[str, str]:
    """Parses the metric number, normalizes the unit, and returns
    a tuple (normalized_digits, metric_multiplier).
    """
    match = METRIC_NUMBER.match(num)
    if not match:
        return num, None
    digits_str, multiplier = match.group(1), match.group(2)
    digits_decimal = Decimal(digits_str)
    digits_decimal *= Decimal(10) ** Decimal(
        multiplier_to_exponent(multiplier))
    digits, exp = best_exponent(digits_decimal, six)
    unit = exponent_to_multiplier(exp)
    if unicode and unit == "u":
        unit = "µ"
    return digits, unit


def format_metric_unit(
        num: str,
        unit: str = "",
        six: bool = False,
        unicode: bool = True,
        allow_range: bool = True) -> str:
    """Normalizes the Metric multiplier on the number, then adds the unit.

    * If there is a suffix on num, moves it to after the unit.
    * If there is a range of numbers, formats each number in the range
      and adds the unit afterwards.
    * If there is no number in num, returns num unchanged.
    * If unicode is True, uses 'µ' for micro instead of 'u'.
    """
    num = num.strip()
    match = METRIC_RANGE.match(num)
    if match:
        if not allow_range:
            raise ValueError("range not allowed")
        # format the range by calling recursively
        num0, num1 = match.group(1), match.group(2)
        suffix = num[match.span()[1]:]
        digits0, exp0 = normalize_metric(num0, six, unicode)
        digits1, exp1 = normalize_metric(num1, six, unicode)
        if exp0 != exp1:
            # different multiplier so use multiplier and unit on both
            return (f"{digits0} {exp0}{unit} - "
                    f"{digits1} {exp1}{unit} {suffix}").rstrip()
        return f"{digits0}-{digits1} {exp0}{unit} {suffix}".rstrip()
    match = METRIC_NUMBER.match(num)
    if not match:
        return num
    suffix = num[match.span(0)[1]:]
    digits, exp = normalize_metric(match.group(), six, unicode)
    return f"{digits} {exp}{unit} {suffix}".rstrip()


if __name__ == "__main__":
    def test(*args):
        print(">>> format_metric_unit", args, sep="")
        print(repr(format_metric_unit(*args)))
    test("2.5-3500", "V")
    test("50n", "F", True)
    test("50M-1000000000000000000000p", "Hz")
    test(".1", "Ω")
    test("2200u", "F", True)
    test("Gain", "Ω")
