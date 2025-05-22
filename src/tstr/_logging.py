from __future__ import annotations

import logging
import typing
from contextlib import contextmanager

from ._template import Interpolation, Template
from ._utils import binder, convert, render

_resetter = None
Renderer = typing.Callable[[Template], str]


class TemplateFormatter(logging.Formatter):
    """
    A custom logging formatter that uses string templates for formatting log messages.
    """
    default_renderer = staticmethod(render)

    @binder
    def execute_callable(intp: Interpolation) -> str:
        value = intp.value() if callable(intp.value) else intp.value
        converted = convert(value, intp.conversion)
        return format(converted, intp.format_spec)

    def __init__(self, renderer: Renderer | None = None, fmt: str | None = None, datefmt: str | None = None) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt, validate=False)
        self.renderer = renderer
        self._shadowed_formatter: logging.Formatter | None = None

    def format(self, record):
        if isinstance(record.msg, Template):
            renderer = self.renderer or self.default_renderer
            record.msg = renderer(record.msg)

        if self._shadowed_formatter is not None:
            return self._shadowed_formatter.format(record)
        else:
            return super().format(record)

    @classmethod
    def shadow(cls, handler: logging.Handler, renderer, **kwargs) -> typing.Self:
        formatter = cls(renderer, **kwargs)
        formatter._shadowed_formatter = handler.formatter
        handler.setFormatter(formatter)
        return formatter


def install(formatter: Renderer | None = None):
    global _resetter
    if _resetter is None:
        logging.basicConfig()
        try:
            handler = logging.root.handlers[0]
        except Exception:
            handler = logging.lastResort
        assert handler is not None, "No default logging handler found. Please configure logging before using install()."
        old_formatter = handler.formatter
        formatter_ = TemplateFormatter(formatter)
        formatter_._shadowed_formatter = old_formatter
        handler.setFormatter(formatter_)
        _resetter = lambda: handler.setFormatter(old_formatter)  # noqa


def uninstall():
    global _resetter
    if _resetter is not None:
        _resetter()
        _resetter = None


@contextmanager
def logging_context(formatter: typing.Callable[[Template], str] = render):
    """
    A context manager that temporarily installs a custom logging formatter.
    """
    install(formatter)
    try:
        yield
    finally:
        uninstall()
