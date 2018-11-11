import re


class Chunk:
    def __init__(self, mantissa=1, multipliers=None):
        self.mantissa = mantissa
        self.multipliers = multipliers or []

    @property
    def value(self):
        value = self.mantissa
        for multiplier in self.multipliers:
            value *= multiplier
        return value

    def __repr__(self):
        return f"{type(self).__name__}({self.value})"


class Multiplier:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{type(self).__name__}({self.value})"


words = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": Multiplier(100),
    "thousand": Multiplier(1000),
    "million": Multiplier(10 ** 6),
    "billion": Multiplier(10 ** 9),
    "trillion": Multiplier(10 ** 12),
    "quadrillion": Multiplier(10 ** 15),
    "quintillion": Multiplier(10 ** 18),
    "sextillion": Multiplier(10 ** 21),
    "septillion": Multiplier(10 ** 24),
    "octillion": Multiplier(10 ** 27),
    "nonillion": Multiplier(10 ** 30),
    "decillion": Multiplier(10 ** 33),
    "undecillion": Multiplier(10 ** 36),
    "duodecillion": Multiplier(10 ** 39),
    "tredecillion": Multiplier(10 ** 42),
    "quattordecillion": Multiplier(10 ** 45),
    "quindecillion": Multiplier(10 ** 48),
    "sexdecillion": Multiplier(10 ** 51),
    "septendecillion": Multiplier(10 ** 54),
    "octodecillion": Multiplier(10 ** 57),
    "novemdecillion": Multiplier(10 ** 60),
    "vigintillion": Multiplier(10 ** 63),
    "centillion": Multiplier(10 ** 303),
    "double": Multiplier(2),
}

prefixes = {
    "deca": Multiplier(10),
    "hecto": Multiplier(100),
    "kilo": Multiplier(1000),
    "mega": Multiplier(10 ** 6),
    "giga": Multiplier(10 ** 9),
    "tera": Multiplier(10 ** 12),
    "peta": Multiplier(10 ** 15),
    "exa": Multiplier(10 ** 18),
    "zetta": Multiplier(10 ** 21),
    "yotta": Multiplier(10 ** 24),
}


def strint(numstring):
    parts = re.findall(
        r"\d+(?:\.\d+)?|[,;]|[a-z]+(?:-[a-z]+)?", numstring, re.IGNORECASE
    )
    first_pass = []
    currently_dealing_with_literal_strings = False
    for part in parts:
        lp = part.lower()
        if lp in (",", ";"):
            continue
        elif lp == "and":
            if currently_dealing_with_literal_strings and isinstance(
                first_pass[-1], str
            ):
                first_pass[-1] += " " + part
            continue
        try:
            first_pass.append(int(part))
            currently_dealing_with_literal_strings = False
            continue
        except ValueError:
            pass
        try:
            first_pass.append(float(part))
            currently_dealing_with_literal_strings = False
            continue
        except ValueError:
            pass
        if lp in words:
            first_pass.append(words[lp])
            currently_dealing_with_literal_strings = False
            continue
        elif lp in prefixes:
            first_pass.append(prefixes[lp])
            continue
        if "-" in lp:
            raw_prefix, raw_suffix = lp.split("-")
            if raw_prefix in words and raw_suffix in words:
                prefix = words[raw_prefix]
                suffix = words[raw_suffix]

                if isinstance(prefix, int) and isinstance(suffix, int):
                    if prefix in (20, 30, 40, 50, 60, 70, 80, 90) and suffix < 10:
                        first_pass.append(prefix + suffix)
                        currently_dealing_with_literal_strings = False
                        continue
                    raise ValueError(f"Unable to parse '{part}'.")
                else:
                    first_pass.append(prefix)
                    first_pass.append(suffix)
                    currently_dealing_with_literal_strings = False
                    continue
            elif raw_prefix in prefixes:
                prefix = prefixes[raw_prefix]
                if raw_suffix in words:
                    suffix = words[raw_suffix]
                    if isinstance(suffix, Multiplier):
                        first_pass.append(suffix)
                        first_pass.append(prefix)
                        currently_dealing_with_literal_strings = False
                        continue
                    raise ValueError(f"Unable to parse '{part}'.")
                elif raw_suffix in prefixes:
                    first_pass.append(prefixes[raw_suffix])
                    first_pass.append(prefix)
                    currently_dealing_with_literal_strings = False
                    continue
                first_pass.append(prefix)
                if currently_dealing_with_literal_strings:
                    first_pass[-1] += " " + raw_suffix
                else:
                    first_pass.append(raw_suffix)
                currently_dealing_with_literal_strings = True
                continue
            if currently_dealing_with_literal_strings:
                first_pass[-1] += " " + part
            else:
                first_pass.append(part)
            currently_dealing_with_literal_strings = True
            continue
        prefixed_match = re.match(
            r"(?P<prefixes>(?:" + "|".join(prefixes.keys()) + r")*)(?P<unit>\w+)", lp
        )
        if prefixed_match:
            if prefixed_match.group("prefixes"):
                for prefix in re.findall(
                    "|".join(prefixes.keys()), prefixed_match.group("prefixes")
                ):
                    first_pass.append(prefixes[prefix])
                    currently_dealing_with_literal_strings = False
            raw_unit = prefixed_match.group("unit")
            if raw_unit in words:
                unit = words[raw_unit]
                if isinstance(unit, Multiplier):
                    first_pass.append(unit)
                    currently_dealing_with_literal_strings = False
                    continue
                raise ValueError(f"Unable to parse '{part}'.")
            if currently_dealing_with_literal_strings:
                first_pass[-1] += " " + raw_unit
            else:
                first_pass.append(raw_unit)
            currently_dealing_with_literal_strings = True
            continue
        if currently_dealing_with_literal_strings:
            first_pass[-1] += " " + part
        else:
            first_pass.append(part)
        currently_dealing_with_literal_strings = True

    second_pass = []
    chunk = None
    for part in first_pass:
        if isinstance(part, (int, float)):
            if chunk is None:
                chunk = Chunk(mantissa=part)
                continue
            else:
                second_pass.append(chunk)
                chunk = Chunk(mantissa=part)
                continue
        elif isinstance(part, Multiplier):
            if chunk is None:
                chunk = Chunk(mantissa=1, multipliers=[part.value])
                continue
            else:
                chunk.multipliers.append(part.value)
                continue
        if chunk:
            second_pass.append(chunk)
            chunk = None
        if isinstance(part, str):
            if part.lower().endswith(" and"):
                part = part[:-4]
        second_pass.append(part)

    if chunk:
        second_pass.append(chunk)

    third_pass = {}
    superchunk = None
    for part in second_pass:
        if isinstance(part, Chunk):
            if superchunk is None:
                superchunk = [part]
            else:
                superchunk.append(part)
        else:
            if superchunk is None:
                continue
            unit = part
            if unit in third_pass:
                third_pass[unit].extend(superchunk)
            else:
                third_pass[unit] = superchunk
            superchunk = None

    if superchunk:
        third_pass[None] = superchunk

    for key, superchunk in third_pass.items():
        third_pass[key] = sum([chunk.value for chunk in superchunk])

    if len(third_pass) == 1 and None in third_pass:
        return third_pass[None]
    else:
        return third_pass
