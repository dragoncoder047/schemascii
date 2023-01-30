import re
from decimal import Decimal

METRIC_NUMBER = re.compile(r"^(\d*\.?\d+)([pnumKkMG]?)$")  # cSpell:ignore pnum
ENG_NUMBER = re.compile(r"^(\d*\.?\d+)[Ee]?([+-]?\d*)$")


def exponent_to_prefix(exponent: int) -> str | None:
    """Turns the 10-power into a Metric prefix.
    E.g.  3 --> "k" (kilo)
    E.g.  0 --> ""  (no prefix)
    E.g. -6 --> "u" (micro)
    If it is not a multiple of 3, returns None."""
    if exponent % 3 != 0:
        return None
    index = (exponent // 3) + 4  # pico is -12 --> 0
    # cSpell:ignore pico
    return "pnum kMG"[index].strip()


def prefix_to_exponent(prefix: int) -> str:
    """Turns the Metric prefix into its exponent.
    E.g. "k" -->  3 (kilo)
    E.g. " " -->  0 (no prefix)
    E.g. "u" --> -6 (micro)"""
    if prefix in (' ', ''):
        return 0
    if prefix == 'K':
        prefix = prefix.lower()  # special case (preferred is lowercase)
    i = "pnum kMG".index(prefix)
    return (i - 4) * 3


def format_metric_unit(num: str, unit: str = '', six: bool = False) -> str:
    "Normalizes the Metric unit on the number."
    num = num.strip()
    match = METRIC_NUMBER.match(num)
    if not match:
        return num
    digits_str, prefix = match.group(1), match.group(2)
    digits_decimal = Decimal(digits_str)
    digits_decimal *= Decimal('10') ** Decimal(prefix_to_exponent(prefix))
    res = ENG_NUMBER.match(digits_decimal.to_eng_string())
    if not res:
        print('foobar!')
        return None
    digits, exp = res.group(1), int(res.group(2) or '0')
    assert exp % 3 == 0, 'failed to make engineering notation'
    if six and exp % 6:
        digits = Decimal(digits)
        nd_1, nd_2, = str(digits * 1000), str(digits / 1000)
        exp_1, exp_2 = exp - 3, exp + 3
        digits = nd_1 if len(nd_1) < len(nd_2) else nd_2
        exp = exp_1 if len(nd_1) < len(nd_2) else exp_2
    out = digits + " " + exponent_to_prefix(exp) + unit
    return out.replace(" u", " &micro;")


if __name__ == '__main__':
    print(format_metric_unit("2.5", "V"))
    print(format_metric_unit("50n", "F", True))
    print(format_metric_unit("1234", "&ohm;"))
    print(format_metric_unit("0.47u", "F", True))
    print(format_metric_unit("Gain", "&ohm;"))
