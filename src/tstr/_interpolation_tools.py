from __future__ import annotations

import typing

from ._template import Conversion, Interpolation

__all__ = [
    "convert",
    "normalize",
    "normalize_str",
    "interpolation_replace",
]

T = typing.TypeVar("T")


@typing.overload
def convert(
    value: typing.Any,
    conversion: Conversion,
) -> str: ...

@typing.overload
def convert(
    value: typing.Any,
    conversion: str,
) -> str: ...

@typing.overload
def convert(
    value: T,
    conversion: Conversion | None,
) -> T | str: ...

@typing.overload
def convert(
    value: T,
    conversion: str | None,
) -> T | str: ...


def convert(
    value: T,
    conversion: str | None,
) -> T | str:
    """
    Applies a conversion to a value, similar to how f-strings handle conversions.

    Args:
        value (T): The value to convert, typically from an Interpolation.value.
        conversion (Conversion | None): The conversion specifier ('a', 'r', or 's'), or None.

    Returns:
        T | str: The value converted according to the specified conversion;
            if 'conversion' is None, returns the original value unchanged.
    """
    if conversion is None:
        return value
    if conversion == "s":
        return str(value)
    if conversion == "r":
        return repr(value)
    if conversion == "a":
        return ascii(value)
    raise ValueError(f"Invalid conversion: {conversion}")


def normalize(interp: Interpolation) -> str | object:
    """
    Normalizes a PEP 750 Interpolation, preserving its type when possible.

    This is a more flexible version of normalize_str() that preserves the original
    value's type when no conversion is specified.

    If neither a conversion nor a format spec is specified, the original value
    is returned without any modification, ensuring that the value's type is preserved.

    Args:
        interp (Interpolation): The interpolation to normalize.

    Returns:
        str | object: The normalized string if conversion or format spec is specified, otherwise
            the original value.
    """
    if interp.conversion or interp.format_spec:
        return normalize_str(interp)
    else:
        return interp.value


def normalize_str(interp: Interpolation) -> str:
    """
    Normalizes a PEP 750 Interpolation to a formatted string.

    This processes an Interpolation object similarly to how f-strings process
    interpolated expressions: it applies conversion and format specification.
    Unlike normalize(), this always returns a string.

    Args:
        interp (Interpolation): The interpolation to normalize.

    Returns:
        str: The formatted string representation of the interpolation.
    """
    converted = convert(interp.value, interp.conversion)
    return format(converted, interp.format_spec)


_NOTSET = object()


def interpolation_replace(
    interp: Interpolation,
    *,
    value: object = _NOTSET,
    expression: str = _NOTSET,  # type: ignore
    conversion: typing.Literal["a", "r", "s"] | None = _NOTSET,  # type: ignore
    format_spec: str = _NOTSET,  # type: ignore
) -> Interpolation:
    """
    Creates a new Interpolation by selectively replacing attributes of an existing one.

    This function allows you to create a modified copy of an Interpolation object
    by specifying which attributes to replace. Any attribute not explicitly provided
    will retain its original value from the input interpolation.

    Args:
        interp (Interpolation): The original interpolation object.
        value (object, optional): New value to use instead of the original.
        expression (str, optional): New expression to use instead of the original.
        conversion (Literal["a", "r", "s"] | None, optional): New conversion to use.
        format_spec (str, optional): New format specification to use.

    Returns:
        Interpolation: A new Interpolation with the specified replacements.
    """
    value = interp.value if value is _NOTSET else value
    expression = interp.expression if expression is _NOTSET else expression
    conversion = interp.conversion if conversion is _NOTSET else conversion
    format_spec = interp.format_spec if format_spec is _NOTSET else format_spec
    return Interpolation(value, expression, conversion, format_spec)  # type: ignore
