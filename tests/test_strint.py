import pytest

from strint import strint, Chunk, PowerOfTen


def test_readme_example_1():
    assert strint("two octillion gigadollars and twelve cents") == {
        "dollars": 2 * (10 ** 27) * (10 ** 9),
        "cents": 12,
    }


def test_readme_example_2():
    assert strint(
        "twenty-three hours, fifty-nine minutes,"
        " 40 short seconds and 20 long seconds"
    ) == {"hours": 23, "minutes": 59, "short seconds": 40, "long seconds": 20}


def test_readme_example_3():
    assert strint("one, two, one two and three and four") == 13


def test_chunk_repr():
    assert repr(Chunk(1, PowerOfTen(10))) == "Chunk(1, 10)"


def test_multiplier_repr():
    assert repr(PowerOfTen(15)) == "PowerOfTen(15)"


def test_prefix_only():
    assert strint("hecto") == 100


def test_reject_prefixed_non_exponent_word():
    with pytest.raises(ValueError):
        _ = strint("megaten")


def test_prefixed_exponent_words():
    assert strint("twelve gigamillion ties and one megagigatrillion and one hats") == {
        "ties": 12 * (10 ** 9) * (10 ** 6),
        "hats": (10 ** 6) * (10 ** 9) * (10 ** 12) + 1,
    }


def test_multiword_units():
    assert strint("99 megamillion bottles of beer on the wall") == {
        "bottles of beer on the wall": 99 * (10 ** 6) * (10 ** 6)
    }


def test_and_stripping():
    assert strint("and one more thing") == {"more thing": 1}
    assert strint("one more thing and") == {"more thing": 1}


def test_multiple_with_same_unit():
    assert strint("one banana and one banana") == {"banana": 2}


def test_hyphen_in_weird_places():
    assert strint("one-million") == 1_000_000


def test_hyphen_in_other_weird_places():
    with pytest.raises(ValueError):
        _ = strint("one-two")


def test_prefix_with_hyphen():
    assert strint("giga-million") == (10 ** 9) * (10 ** 6)


def test_hyphen_thing_consisting_of_two_prefixes():
    assert strint("tera-mega") == (10 ** 12) * (10 ** 6)


def test_prefixed_unit_with_hyphen():
    assert strint("mega-fun") == {"fun": 1_000_000}


def test_prefixed_number_with_hyphen():
    with pytest.raises(ValueError):
        _ = strint("kilo-twenty")


def test_some_string_thing():
    assert strint("which one of these three") == {None: 3, "of these": 1}


def test_hyphenated_words_with_no_numeric_significance():
    assert strint("five test-cases") == {"test-cases": 5}
    assert strint("a million bad bug-reports") == {"bad bug-reports": 1_000_000}


def test_and_after_parsed_token():
    assert strint("five and ten") == 15


def test_and_in_unit_name():
    assert strint("forty evil and roids") == {"evil and roids": 40}


def test_bigger_part_followed_by_smaller_and_then_bigger_again():
    assert strint("two hundred and ninety-one thousand") == 291_000
