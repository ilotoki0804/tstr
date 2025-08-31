from __future__ import annotations

import typing
from itertools import zip_longest

__all__ = ["Template", "Interpolation"]


@typing.final
class Template:
    __strings: tuple[str, ...]
    __interpolations: tuple[Interpolation, ...]

    @property
    def strings(self) -> tuple[str, ...]:
        """
        A non-empty tuple of the string parts of the template,
        with N+1 items, where N is the number of interpolations
        in the template.
        """
        return self.__strings

    @property
    def interpolations(self) -> tuple[Interpolation, ...]:
        """
        A tuple of the interpolation parts of the template.
        This will be an empty tuple if there are no interpolations.
        """
        return self.__interpolations

    def __init__(self, *args: str | Interpolation) -> None:
        """
        Create a new Template instance.

        Arguments can be provided in any order.
        """
        str_last_added = False
        strings = []
        interpolations = []
        for item in args:
            if isinstance(item, str):
                if str_last_added:
                    strings[-1] += item
                else:
                    strings.append(item)
                str_last_added = True
            elif isinstance(item, Interpolation):
                if not str_last_added:
                    strings.append("")
                interpolations.append(item)
                str_last_added = False
            else:
                raise TypeError(
                    f"Template.__new__ *args need to be of type 'str' or 'Interpolation', got {type(item).__name__}"
                )

        if len(strings) == len(interpolations):
            strings.append("")

        self.__strings = tuple(strings)
        self.__interpolations = tuple(interpolations)

    @property
    def values(self) -> tuple[object, ...]:
        """
        Return a tuple of the `value` attributes of each Interpolation
        in the template.
        This will be an empty tuple if there are no interpolations.
        """
        return tuple(interpolation.value for interpolation in self.interpolations)

    def __iter__(self) -> typing.Iterator[str | Interpolation]:
        """
        Iterate over the string parts and interpolations in the template.

        These may appear in any order. Empty strings will not be included.
        """
        for string, interpolation in zip_longest(self.strings, self.interpolations):
            if string:
                yield string
            if interpolation:
                yield interpolation

    def __add__(self, other: str | Template) -> Template:
        if isinstance(other, str):
            raise TypeError(
                'can only concatenate tstr.Template (not "str") to tstr.Template')
        elif isinstance(other, Template):
            return Template(*self, *other)
        else:
            return NotImplemented

    def __radd__(self, other: str | Template) -> Template:
        if isinstance(other, str):
            raise TypeError(
                'can only concatenate str (not "tstr.Template") to str')
        elif isinstance(other, Template):
            return Template(*other, *self)
        else:
            return NotImplemented

    def __repr__(self) -> str:
        return f"Template(strings={self.strings!r}, interpolations={self.interpolations!r})"


@typing.final
class Interpolation:
    __match_args__ = ("value", "expression", "conversion", "format_spec")
    __value: object
    __expression: str
    __conversion: typing.Literal["a", "r", "s"] | None
    __format_spec: str

    @property
    def value(self) -> object:
        return self.__value

    @property
    def expression(self) -> str:
        return self.__expression

    @property
    def conversion(self) -> typing.Literal["a", "r", "s"] | None:
        return self.__conversion

    @property
    def format_spec(self) -> str:
        return self.__format_spec

    def __init__(
        self,
        value: object,
        expression: str,
        conversion: typing.Literal["a", "r", "s"] | None = None,
        format_spec: str = "",
    ) -> None:
        self.__value = value
        if conversion not in (None, "a", "r", "s"):
            raise ValueError(
                f"Interpolation() argument 'conversion' must be one of 's', 'a' or 'r'"
            )
        self.__expression = expression
        self.__conversion = conversion
        self.__format_spec = format_spec

    def __repr__(self) -> str:
        return f"Interpolation({self.value!r}, {self.expression!r}, {self.conversion!r}, {self.format_spec!r})"
