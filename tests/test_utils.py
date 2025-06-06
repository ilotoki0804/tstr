# type: ignore

from __future__ import annotations

import inspect

import pytest

from tstr import (
    CONVERTERS,
    Template,
    bind,
    binder,
    convert,
    f,
    generate_template,
    interpolation_replace,
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


def test_use_eval():
    val = "value"

    template = t("{42!s} {val}", use_eval=True)
    assert f(template) == "42 value"

    with pytest.raises(KeyError):
        template = t("{42!s} {val}", use_eval=False)

    template = t("{val} text", use_eval=True)
    assert f(template) == "value text"

    template = t("{val} text", use_eval=False)
    assert f(template) == "value text"

    template = t("{42} {val}")
    assert f(template) == "42 value"

    with pytest.raises(KeyError):
        t("{42} {con}", context=dict(con="text"))

    with pytest.raises(KeyError):
        t("{42} {con}", globals=dict(con="text"))

    template = t("{42} {con}", context=dict(con="text"), use_eval=True)
    assert f(template) == "42 text"

    template = t("{42} {con}", globals=dict(con="text"), use_eval=True)
    assert f(template) == "42 text"


def test_interpolation_replace():
    """Test the interpolation_replace function with various replacement scenarios."""
    # Setup a template with an interpolation
    name = "world"
    template = generate_template("Hello {name:>10}!")
    orig_interp = template.interpolations[0]

    # Test replacing just the value
    new_interp = interpolation_replace(orig_interp, value="universe")
    assert new_interp.value == "universe"
    assert new_interp.expression == orig_interp.expression
    assert new_interp.format_spec == ">10"
    assert new_interp.conversion == orig_interp.conversion

    # Test replacing just the format specification
    new_interp = interpolation_replace(orig_interp, format_spec="^20")
    assert new_interp.value == "world"
    assert new_interp.format_spec == "^20"
    assert new_interp.expression == orig_interp.expression

    # Test replacing just the conversion
    new_interp = interpolation_replace(orig_interp, conversion="r")
    assert new_interp.conversion == "r"
    assert f(Template("", new_interp)) == "   'world'"

    # Test replacing just the expression (expression changes don't affect evaluation)
    new_interp = interpolation_replace(orig_interp, expression="new_name")
    assert new_interp.expression == "new_name"
    assert new_interp.value == "world"  # Value remains unchanged

    # Test replacing multiple attributes
    new_interp = interpolation_replace(
        orig_interp,
        value=123,
        format_spec=".2f",
    )
    assert new_interp.value == 123
    assert new_interp.format_spec == ".2f"
    assert f(Template("", new_interp)) == "123.00"

    # Verify original interpolation is not modified
    assert orig_interp.value == "world"
    assert orig_interp.format_spec == ">10"
    assert orig_interp.conversion is None

    # Test with complex combinations
    numeric_value = 42
    orig_template = generate_template("Value: {numeric_value:.1f}")
    orig_numeric_interp = orig_template.interpolations[0]

    # Change numeric value with different format
    new_interp = interpolation_replace(
        orig_numeric_interp,
        value=3.14159,
        format_spec=".4f"
    )
    assert f(Template("", new_interp)) == "3.1416"

    # Change to different conversion
    new_interp = interpolation_replace(orig_numeric_interp, conversion="r", format_spec="")
    assert f(Template("", new_interp)) == "42"  # repr of 42 is just "42"


def test_generate_template_with_frame():
    """Test the frame parameter of generate_template function."""

    # Outer function with a local variable
    def outer_function():
        outer_var = "outer scope value"

        # Inner function that needs to access outer_var
        def inner_function():
            inner_var = "inner scope value"

            # Get the outer function's frame
            outer_frame = inspect.currentframe().f_back

            # Using current frame (default behavior)
            template1 = generate_template("Inner: {inner_var}")

            # Using explicit outer frame to access outer_var
            template2 = generate_template("Outer: {outer_var}", frame=outer_frame)

            # This would fail without the frame parameter
            # since inner_function doesn't have access to outer_var
            with pytest.raises(NameError):
                template_fail = generate_template("Outer: {outer_var}")

            return template1, template2

        return inner_function()

    # Call the outer function to run the test
    template1, template2 = outer_function()

    # Verify results
    from tstr import f
    assert f(template1) == "Inner: inner scope value"
    assert f(template2) == "Outer: outer scope value"


def test_frame_hierarchy():
    """Test accessing variables from different levels of the call stack."""

    def level1():
        var1 = "level 1 variable"

        def level2():
            var2 = "level 2 variable"

            def level3():
                var3 = "level 3 variable"

                # Get frames from different levels
                current_frame = inspect.currentframe()
                level2_frame = current_frame.f_back
                level1_frame = level2_frame.f_back

                # Access variables from different frames
                template1 = generate_template("L1: {var1}", frame=level1_frame)
                template2 = generate_template("L2: {var2}", frame=level2_frame)
                template3 = generate_template("L3: {var3}")  # Uses current frame

                return template1, template2, template3

            return level3()

        return level2()

    # Run the nested functions
    template1, template2, template3 = level1()

    # Verify results
    from tstr import f
    assert f(template1) == "L1: level 1 variable"
    assert f(template2) == "L2: level 2 variable"
    assert f(template3) == "L3: level 3 variable"
