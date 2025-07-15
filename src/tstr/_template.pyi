from __future__ import annotations

import sys
import typing

__all__ = ["Template", "Interpolation", "Conversion"]

Conversion: typing.TypeAlias = typing.Literal["a", "r", "s"]

if sys.version_info >= (3, 14):
    TEMPLATE_STRING_SUPPORTED = True
    StringOrTemplate: typing.TypeAlias = typing.LiteralString | Template

    from string.templatelib import Interpolation, Template

else:
    TEMPLATE_STRING_SUPPORTED = False
    StringOrTemplate: typing.TypeAlias = str | Template

    from ._compat import Interpolation, Template
