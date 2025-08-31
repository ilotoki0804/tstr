from __future__ import annotations

import logging
import typing
from contextlib import contextmanager

from tstr import Interpolation, Template, binder, convert, render

__all__ = ["TemplateFormatter", "install", "logging_context", "uninstall"]

_resetter = None
Renderer = typing.Callable[[Template], str]


class TemplateFormatter(logging.Formatter):
    """
    A logging formatter that supports template-based string formatting for log messages.

    This formatter extends the standard logging.Formatter to handle Template objects
    in log messages. When a log record's message is a Template object, it uses the
    provided renderer (or the default_renderer) to convert the template into a string
    before further formatting.

    Attributes:
        default_renderer (staticmethod): Default method to render Template objects.

    Methods:
        execute_callable: Processes an interpolation by executing callables, converting
                         values, and applying format specifications.
        format: Overrides the standard format method to handle Template objects.
        shadow: Class method that replaces a handler's formatter with an instance of
                this class while preserving the original formatter.

    Args:
        renderer (Renderer, optional): Function to render Template objects. If None,
                                      default_renderer is used. Defaults to None.
        fmt (str, optional): Format string for log messages. Defaults to None.
        datefmt (str, optional): Format string for dates. Defaults to None.
    """
    default_renderer = staticmethod(render)

    @staticmethod
    @binder
    def execute_callable(interp: Interpolation) -> str:
        value = interp.value() if callable(interp.value) else interp.value
        converted = convert(value, interp.conversion)
        return format(converted, interp.format_spec)

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
    """
    Install template formatter at global logger. This function is idempotent.
    """
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
    """
    Remove template formatter at global logger if exists. This function is idempotent.
    """
    global _resetter
    if _resetter is not None:
        try:
            _resetter()
        finally:
            _resetter = None


@contextmanager
def logging_context(formatter: typing.Callable[[Template], str] | None = None):
    """
    A context manager that temporarily installs a template formatter.
    """
    install(formatter)
    try:
        yield
    finally:
        uninstall()
