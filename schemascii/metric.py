import re
from decimal import Decimal

METRIC_NUMBER = re.compile(r"^(\d*\.?\d+)([pnumKkMG]?)$")  # cSpell:ignore pnum


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
    _, digits, exp = digits_decimal.as_tuple()
    sig_figs = len(digits)
    three_six = 6 if six else 3
    two_five = 5 if six else 2
    while digits[-three_six:] == (0,) * three_six:
        digits = digits[:-three_six]
        exp += three_six
    digits += (0,) * (exp % 3)
    exp -= exp % 3
    while digits[-three_six:] == (0,) * three_six:
        digits = digits[:-three_six]
        exp += three_six
    if six and exp % 6 != 0 and exp < 0:
        digits += (0, 0, 0)
        exp -= 3
    exp += prefix_to_exponent(prefix)
    print(digits, exp)
    digits_str = ''.join(map(str, digits))
    if digits_str.endswith('0' * two_five) and exp < 0:
        digits_str = digits_str[:-three_six] + '.' + digits_str[-three_six:]
        exp += three_six
        sig_figs += 1
        if len(digits_str) > sig_figs:
            digits_str = digits_str.removesuffix('0' * (len(digits_str)
                                                        - sig_figs))
    out = digits_str + " " + exponent_to_prefix(exp) + unit
    return out.replace(" u", " &micro;")


if __name__ == '__main__':
    print(format_metric_unit("2.5", "V"))
    print(format_metric_unit("0.05", "F", True))
    print(format_metric_unit("1234", "&ohm;"))
    print(format_metric_unit("0.47u", "F", True))
    print(format_metric_unit("Gain", "&ohm;"))
