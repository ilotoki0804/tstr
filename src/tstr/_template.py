from __future__ import annotations

import typing

__all__ = ["Template", "Interpolation", "Conversion", "TEMPLATE_STRING_SUPPORTED", "StringOrTemplate"]

Conversion: typing.TypeAlias = typing.Literal["a", "r", "s"]

try:
    from string.templatelib import Interpolation, Template  # type: ignore

    TEMPLATE_STRING_SUPPORTED = True
    StringOrTemplate: typing.TypeAlias = typing.LiteralString | Template  # type: ignore
except Exception:
    # Fallback to compatible implementation if template strings are not supported
    from ._compat import Interpolation, Template

    TEMPLATE_STRING_SUPPORTED = False
    StringOrTemplate: typing.TypeAlias = str | Template  # type: ignore
