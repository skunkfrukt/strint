from collections import namedtuple
import itertools
import re

VERSION = "0.0.1"

Slab = namedtuple("Slab", "value unit")


class Chunk:
    def __init__(self, digit=None, power=None):
        self.digit = digit
        self.power = power

    @property
    def value(self):
        if self.digit is not None and self.power:
            return self.digit * self.power.value
        return None

    def __str__(self):
        if self.digit is None:
            digit_repr = "?"
        else:
            digit_repr = self.digit

        if self.power is None:
            power_repr = "?"
        else:
            power_repr = self.power.exponent
        return f"{digit_repr}e{power_repr}"

    def __repr__(self):
        if self.digit is None:
            digit_repr = "?"
        else:
            digit_repr = self.digit

        if self.power is None:
            power_repr = "?"
        else:
            power_repr = self.power.exponent

        return f"{type(self).__name__}({digit_repr}, {power_repr})"


class ChainChunk:
    def __init__(self, *chunks):
        self.chunks = list(chunks)
        self.unit = None

    def add_chunk(self, chunk):
        self.chunks.append(chunk)

    @property
    def minpower(self):
        return self.chunks[-1].power

    @property
    def maxpower(self):
        return self.chunks[0].power

    def __repr__(self):
        return f"{type(self).__name__}({self.chunks}, {self.unit or '-'})"

    def flatten(self):
        value = sum([chunk.value for chunk in self.chunks])
        if self.unit:
            unit = self.unit.name
            if unit.lower().endswith(" and"):
                unit = unit[:-4]
            return Slab(value, unit)
        return Slab(value, None)

    def split_at_power(self, power):
        keep_these = reversed(
            list(
                itertools.dropwhile(
                    lambda chunk: chunk.power < power, reversed(self.chunks)
                )
            )
        )
        give_these = reversed(
            list(
                itertools.takewhile(
                    lambda chunk: chunk.power < power, reversed(self.chunks)
                )
            )
        )

        return ChainChunk(*keep_these), ChainChunk(*give_these)


class PowerOfTen:
    def __init__(self, exponent, prefix=False):
        self.exponent = exponent
        self.prefix = prefix

    @property
    def value(self):
        return 10 ** self.exponent

    def __str__(self):
        return f"10^{self.exponent}"

    def __repr__(self):
        return f"{type(self).__name__}({self.exponent})"

    def __mul__(self, other):
        return PowerOfTen(self.exponent + other.exponent)

    def __lt__(self, other):
        return self.exponent < other.exponent

    def __gt__(self, other):
        return self.exponent > other.exponent


class Unit:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Unit({self.name})"

    def __add__(self, s):
        return Unit(self.name + s)


class And:
    pass


words = {
    "zero": 0,
    "one": 1,
    "a": 1,
    "an": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": (1, PowerOfTen(1)),
    "eleven": (1, PowerOfTen(1), 1),
    "twelve": (1, PowerOfTen(1), 2),
    "thirteen": (1, PowerOfTen(1), 3),
    "fourteen": (1, PowerOfTen(1), 4),
    "fifteen": (1, PowerOfTen(1), 5),
    "sixteen": (1, PowerOfTen(1), 6),
    "seventeen": (1, PowerOfTen(1), 7),
    "eighteen": (1, PowerOfTen(1), 8),
    "nineteen": (1, PowerOfTen(1), 9),
    "twenty": (2, PowerOfTen(1)),
    "thirty": (3, PowerOfTen(1)),
    "forty": (4, PowerOfTen(1)),
    "fifty": (5, PowerOfTen(1)),
    "sixty": (6, PowerOfTen(1)),
    "seventy": (7, PowerOfTen(1)),
    "eighty": (8, PowerOfTen(1)),
    "ninety": (9, PowerOfTen(1)),
    "hundred": PowerOfTen(2),
    "thousand": PowerOfTen(3),
    "million": PowerOfTen(6),
    "billion": PowerOfTen(9),
    "trillion": PowerOfTen(12),
    "quadrillion": PowerOfTen(15),
    "quintillion": PowerOfTen(18),
    "sextillion": PowerOfTen(21),
    "septillion": PowerOfTen(24),
    "octillion": PowerOfTen(27),
    "nonillion": PowerOfTen(30),
    "decillion": PowerOfTen(33),
    "undecillion": PowerOfTen(36),
    "duodecillion": PowerOfTen(39),
    "tredecillion": PowerOfTen(42),
    "quattordecillion": PowerOfTen(45),
    "quindecillion": PowerOfTen(48),
    "sexdecillion": PowerOfTen(51),
    "septendecillion": PowerOfTen(54),
    "octodecillion": PowerOfTen(57),
    "novemdecillion": PowerOfTen(60),
    "vigintillion": PowerOfTen(63),
    "centillion": PowerOfTen(303),
}

prefixes = {
    "deca": PowerOfTen(1, prefix=True),
    "hecto": PowerOfTen(2, prefix=True),
    "kilo": PowerOfTen(3, prefix=True),
    "mega": PowerOfTen(6, prefix=True),
    "giga": PowerOfTen(9, prefix=True),
    "tera": PowerOfTen(12, prefix=True),
    "peta": PowerOfTen(15, prefix=True),
    "exa": PowerOfTen(18, prefix=True),
    "zetta": PowerOfTen(21, prefix=True),
    "yotta": PowerOfTen(24, prefix=True),
}


def strint(numstring):
    parts = re.findall(
        r"\d+(?:\.\d+)?|[,;]|[a-z]+(?:-[a-z]+)?", numstring, re.IGNORECASE
    )[::-1]

    def previous_token_is_unit() -> bool:
        return first_pass and isinstance(first_pass[-1], Unit)

    def axpend(list_, item):
        if isinstance(item, (list, tuple)):
            list_.extend(item)
        else:
            list_.append(item)

    first_pass = []
    while parts:
        part = parts.pop()
        if isinstance(part, Unit):
            if previous_token_is_unit():
                first_pass[-1] += f" {part.name}"
            else:
                first_pass.append(part)
            continue
        if part.isdigit():
            if len(part) == 1:
                first_pass.append(int(part))
                continue
            for power, digit in enumerate(part[::-1]):
                first_pass.append(int(digit))
                first_pass.append(PowerOfTen(power))
            continue
        lp = part.lower()
        if lp in (",", ";"):
            continue
        if lp == "and":
            if previous_token_is_unit():
                first_pass[-1] += f" {part}"
            continue
        if lp in words:
            axpend(first_pass, words[lp])
            continue
        elif lp in prefixes:
            first_pass.append(prefixes[lp])
            continue
        if "-" in lp:
            stuff_to_put_back_in = []
            stuff_that_should_stay_hyphenated = []
            subparts = part.split("-")
            for subpart in subparts:
                lsp = subpart.lower()
                if lsp in words or lsp in prefixes:
                    if stuff_that_should_stay_hyphenated:
                        stuff_to_put_back_in.append(
                            Unit("-".join(stuff_that_should_stay_hyphenated))
                        )
                        stuff_that_should_stay_hyphenated = []
                    stuff_to_put_back_in.append(lsp)
                else:
                    stuff_that_should_stay_hyphenated.append(subpart)
            if stuff_that_should_stay_hyphenated:
                stuff_to_put_back_in.append(
                    Unit("-".join(stuff_that_should_stay_hyphenated))
                )
            if stuff_to_put_back_in:
                parts.extend(stuff_to_put_back_in[::-1])
            continue
        prefixed_match = re.match(
            r"(?P<prefixes>(?:"
            + "|".join([f"{p}-?" for p in prefixes.keys()])
            + r"-?)+)(?P<suffix>\w+)",
            lp,
        )
        if prefixed_match:
            total_prefix_multiplier = PowerOfTen(1)
            for prefix in re.findall(
                "|".join(prefixes.keys()), prefixed_match.group("prefixes")
            ):
                total_prefix_multiplier *= prefixes[prefix.strip("-")]
            raw_suffix = prefixed_match.group("suffix")
            if raw_suffix in words:
                suffix = words[raw_suffix]
                if isinstance(suffix, PowerOfTen):
                    total_prefix_multiplier *= suffix
                    first_pass.append(total_prefix_multiplier)
                    continue
                raise ValueError(f"Unable to parse '{part}'.")
            first_pass.append(total_prefix_multiplier)
            first_pass.append(Unit(raw_suffix))
            continue
        if previous_token_is_unit():
            first_pass[-1] += f" {part}"
        else:
            first_pass.append(Unit(part))

    print(f"* First pass: {first_pass}")

    second_pass = []
    prev_chunk = None
    current_chunk = None
    prefix_multiplier = None
    for part in first_pass:
        # Parts can be int, Unit or PowerOfTen
        if isinstance(part, int):
            if prefix_multiplier:
                raise ValueError("No SI prefixes before ints, please.")
            # An int always marks a new chunk.
            if current_chunk:
                if not current_chunk.power:
                    current_chunk.power = PowerOfTen(0)
                second_pass.append(current_chunk)
                prev_chunk = current_chunk
            current_chunk = Chunk(digit=part)
        elif isinstance(part, PowerOfTen):
            if part.prefix:
                if not prefix_multiplier:
                    prefix_multiplier = PowerOfTen(0)
                prefix_multiplier *= part
                continue
            # A PowerOfTen always ends the current chunk.
            if prefix_multiplier:
                part *= prefix_multiplier
                prefix_multiplier = None
            if current_chunk:
                if prev_chunk and prev_chunk.power < part:
                    current_chunk.power = PowerOfTen(0)
                    second_pass.append(current_chunk)
                    prev_chunk = current_chunk
                    current_chunk = Chunk(power=part)
                else:
                    current_chunk.power = part
            else:
                current_chunk = Chunk(power=part)
            second_pass.append(current_chunk)
            prev_chunk = current_chunk
            current_chunk = None
        elif isinstance(part, Unit):
            if current_chunk:
                if not current_chunk.power:
                    current_chunk.power = PowerOfTen(0)
                if prefix_multiplier:
                    current_chunk.power *= prefix_multiplier
                second_pass.append(current_chunk)
                prev_chunk = current_chunk
                current_chunk = None
            elif prefix_multiplier:
                second_pass.append(Chunk(power=prefix_multiplier))
                prefix_multiplier = None
            second_pass.append(part)
        else:
            raise ValueError(f"Expected int, PowerOfTen or Unit; got '{part}'")
    if current_chunk:
        if not current_chunk.power:
            current_chunk.power = PowerOfTen(0)
        second_pass.append(current_chunk)

    print(f"* Second pass: {second_pass}")

    third_pass = []
    current_chainchunk = None
    for part in second_pass:
        # Parts can only be Chunk or Unit
        if isinstance(part, Chunk):
            if current_chainchunk:
                if current_chainchunk.minpower > part.power:
                    current_chainchunk.add_chunk(part)
                elif current_chainchunk.maxpower > part.power:
                    current_chainchunk, new_chainchunk = current_chainchunk.split_at_power(
                        part.power
                    )
                    third_pass.append(current_chainchunk)
                    third_pass.append(new_chainchunk)
                    current_chainchunk = ChainChunk(part)
                else:
                    third_pass.append(current_chainchunk)
                    current_chainchunk = ChainChunk(part)
            else:
                current_chainchunk = ChainChunk(part)
        elif isinstance(part, Unit):
            if current_chainchunk:
                if current_chainchunk.unit:
                    raise ValueError(
                        f"Didn't expect {current_chainchunk}"
                        f" to have a Unit yet: '{part}'"
                    )
                else:
                    current_chainchunk.unit = part
                    third_pass.append(current_chainchunk)
                    current_chainchunk = None
            else:
                f"Didn't expect a Unit when there is no number: '{part}'"
        else:
            raise ValueError(f"Expected Chunk or Unit; got '{part}'")
    if current_chainchunk:
        third_pass.append(current_chainchunk)

    print(f"* Third pass: {third_pass}")

    fourth_pass = []
    current_slab = None
    for part in third_pass:
        # Parts can only be ChainChunk at this point.
        if isinstance(part, ChainChunk):
            if current_slab:
                if part.chunks[0].digit:
                    fourth_pass.append(current_slab)
                    current_slab = None
                else:
                    part.chunks[0].digit = current_slab.value
                    current_slab = None
            for chunk in part.chunks:
                if not chunk.digit:
                    chunk.digit = 1
            slab = part.flatten()
            if slab.unit:
                fourth_pass.append(slab)
            else:
                current_slab = slab
        else:
            raise ValueError(f"Expected ChainChunk; got '{part}'")
    if current_slab:
        fourth_pass.append(current_slab)

    print(f"* Fourth pass: {fourth_pass}")

    fifth_pass = {}
    for slab in fourth_pass:
        if slab.unit in fifth_pass:
            fifth_pass[slab.unit] += slab.value
        else:
            fifth_pass[slab.unit] = slab.value

    if len(fifth_pass) == 0:
        return None
    elif len(fifth_pass) == 1 and None in fifth_pass:
        return fifth_pass[None]
    return fifth_pass
