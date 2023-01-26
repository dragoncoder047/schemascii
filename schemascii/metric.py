import re
from decimal import Decimal, localcontext

METRIC_NUMBER = re.compile(r"(\d*\.?\d*)([pnumKkMG]?)")  # cSpell:ignore pnum


def exponent_to_prefix(exponent: int) -> str | None:
    """Turns the 10-power into a Metric prefix.
    E.g.  3 --> "k" (kilo)
    E.g.  0 --> ""  (no prefix)
    E.g. -6 --> "u" (micro)
    If it is not a multiple of 3, returns None."""
    if exponent % 3 != 0:
        return None
    index = (exponent // 3) + 4  # pico is -12 --> 0
    return "pnum kMG"[index].strip()


def prefix_to_exponent(prefix: int) -> str:
    """Turns the Metric prefix into its exponent.
    E.g. "k" -->  3 (kilo)
    E.g. " " -->  0 (no prefix)
    E.g. "u" --> -6 (micro)"""
    if prefix in (' ', ''):
        return 0
    if prefix == 'K':
        return 3  # special case (preferred is lowercase)
    i = "pnum kMG".index(prefix)
    return (i - 4) * 3


def format_metric_unit(num: str, unit: str = '') -> str:
    num = num.strip()
    match = METRIC_NUMBER.match(num)
    if not match or not match.group(1):
        return num
    digits_str, prefix = match.group(1), match.group(2)
    digits_decimal = Decimal(digits_str)
    _, digits, exp = digits_decimal.as_tuple()
    while digits[-3:] == (0, 0, 0):
        digits = digits[:-3]
        exp += 3
    digits += (0,) * (exp % 3)
    exp -= exp % 3
    while digits[-3:] == (0, 0, 0):
        digits = digits[:-3]
        exp += 3
    exp += prefix_to_exponent(prefix)
    digits_str = ''.join(map(str, digits))
    if exp < 0:
        while digits_str.endswith('00') and exp < 0:
            digits_str = digits_str[:-3] + '.' + digits_str[-3]
            exp += 3
    else:
        while digits_str.endswith('00'):
            digits_str = digits_str[:-3] + '.' + digits_str[-3]
            exp += 3
    return digits_str + " " + exponent_to_prefix(exp) + unit


if __name__ == '__main__':
    print(format_metric_unit("15", "A"))
    print(format_metric_unit("0.00005", "F"))
    print(format_metric_unit("1234", "&ohm;"))
    print(format_metric_unit("0.47u", "F"))
    print(format_metric_unit("Gain", "&ohm;"))
