# type: ignore

from __future__ import annotations

import pytest

from tstr import (
    CONVERTERS,
    bind,
    binder,
    convert,
    f,
    normalize,
    normalize_str,
    t,
    template_eq,
)


def test_converter_repr_conversion():
    assert CONVERTERS["r"](42) == repr(42)


def test_converter_str_conversion():
    assert CONVERTERS["s"](42) == str(42)


def test_converter_invalid_conversion():
    with pytest.raises(KeyError):
        CONVERTERS["invalid"]  # type: ignore


def test_convert_no_conversion():
    assert convert(42, None) == 42


def test_convert_with_conversion():
    assert convert(42, "s") == "42"


def test_normalize_str():
    template = t("{42!s:>5}")
    interpolation = template.interpolations[0]
    assert normalize_str(interpolation) == "   42"


def test_normalize_no_conversion():
    template = t("{42}")
    interpolation = template.interpolations[0]
    assert normalize(interpolation) == 42


def test_normalize_with_conversion():
    template = t("{42!s:>5}")
    interpolation = template.interpolations[0]
    assert normalize(interpolation) == "   42"


def test_bind():
    template = t("{42!s}text")
    result = bind(template, normalize_str)
    assert result == "42text"


def test_binder():
    template = t("{42!s}text")
    bound = binder(normalize_str)
    result = bound(template)
    assert result == "42text"


def test_f_with_string():
    with pytest.raises(TypeError):
        f("text")


def test_f_with_template():
    template = t("{42!s}text")
    assert f(template) == "42text"


def test_template_eq_identical_templates():
    template1 = t("Hello {42}")
    template2 = t("Hello {42}")
    assert template_eq(template1, template2)


def test_template_eq_different_strings():
    template1 = t("Hello {42}")
    template2 = t("Hi {42}")
    assert not template_eq(template1, template2)


def test_template_eq_different_values():
    template1 = t("Hello {42}")
    template2 = t("Hello {43}")
    assert not template_eq(template1, template2)
    assert template_eq(template1, template2, compare_value=False, compare_expr=False)


def test_template_eq_different_expressions():
    name1, name2 = "world", "world"
    template1 = t("Hello {name1}")
    template2 = t("Hello {name2}")
    assert not template_eq(template1, template2)
    assert template_eq(template1, template2, compare_expr=False)


def test_template_eq_different_format_specs():
    template1 = t("Pi: {3.14159:.2f}")
    template2 = t("Pi: {3.14159:.3f}")
    assert not template_eq(template1, template2)


def test_template_eq_multiple_interpolations():
    first, last = "John", "Doe"
    age = 30
    template1 = t("Name: {first} {last}, Age: {age}")
    template2 = t("Name: {first} {last}, Age: {age}")
    age = 31
    template3 = t("Name: {first} {last}, Age: {age}")

    assert template_eq(template1, template2)
    assert not template_eq(template1, template3)
    assert template_eq(template1, template3, compare_value=False)
