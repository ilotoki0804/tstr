from __future__ import annotations

import sys
import typing

__all__ = ["Template", "Interpolation", "Conversion"]

Conversion: typing.TypeAlias = typing.Literal["a", "r", "s"]

if sys.version_info >= (3, 14):
    TEMPLATE_STRING_SUPPORTED = True
    StringOrTemplate: typing.TypeAlias = typing.LiteralString | Template
else:
    TEMPLATE_STRING_SUPPORTED = False
    StringOrTemplate: typing.TypeAlias = str | Template

@typing.runtime_checkable
class Template(typing.Protocol):
    @property
    def strings(self) -> tuple[str, ...]:
        """
        A non-empty tuple of the string parts of the template,
        with N+1 items, where N is the number of interpolations
        in the template.
        """
    @property
    def interpolations(self) -> tuple[Interpolation, ...]:
        """
        A tuple of the interpolation parts of the template.
        This will be an empty tuple if there are no interpolations.
        """
    def __new__(cls, *args: str | Interpolation):
        """
        Create a new Template instance.

        Arguments can be provided in any order.
        """
    @property
    def values(self) -> tuple[object, ...]:
        """
        Return a tuple of the `value` attributes of each Interpolation
        in the template.
        This will be an empty tuple if there are no interpolations.
        """
    def __iter__(self) -> typing.Iterator[str | Interpolation]:
        """
        Iterate over the string parts and interpolations in the template.

        These may appear in any order. Empty strings will not be included.
        """
    def __add__(self, other: str | Template) -> Template: ...
    def __radd__(self, other: str | Template) -> Template: ...

@typing.runtime_checkable
class Interpolation(typing.Protocol):
    __match_args__ = ("value", "expression", "conversion", "format_spec")

    @property
    def value(self) -> object: ...
    @property
    def expression(self) -> str: ...
    @property
    def conversion(self) -> typing.Literal["a", "r", "s"] | None: ...
    @property
    def format_spec(self) -> str: ...
    def __new__(
        cls,
        value: object,
        expression: str,
        conversion: typing.Literal["a", "r", "s"] | None = None,
        format_spec: str = "",
    ): ...
