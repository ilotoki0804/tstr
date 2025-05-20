from __future__ import annotations

import inspect
import types
import typing
from string import Formatter

from ._template import Conversion, Interpolation, Template

__all__ = [
    "bind",
    "binder",
    "f",
    "render",
    "convert",
    "CONVERTERS",
    "normalize",
    "normalize_str",
    "generate_template",
    "TemplateGenerationError",
    "template_eq",
]

_formatter = Formatter()
T = typing.TypeVar("T")
U = typing.TypeVar("U")

CONVERTERS = {
    "a": ascii,
    "r": repr,
    "s": str,
}


class TemplateGenerationError(Exception):
    """
    Exception raised when a template cannot be generated.
    """


def convert(
    value: T,
    conversion: Conversion | None,
) -> T | str:
    """
    Applies a conversion to a value, similar to how f-strings handle conversions.

    Args:
        value (T): The value to convert, typically from an Interpolation.value.
        conversion (Conversion | None): The conversion specifier ('a', 'r', or 's'), or None.

    Returns:
        str: The value converted according to the specified conversion;
            if 'conversion' is None, returns the original value unchanged.
    """
    return CONVERTERS[conversion](value) if conversion else value


def normalize_str(intp: Interpolation) -> str:
    """
    Normalizes a PEP 750 Interpolation to a formatted string.

    This processes an Interpolation object similarly to how f-strings process
    interpolated expressions: it applies conversion and format specification.
    Unlike normalize(), this always returns a string.

    Args:
        interpolation (Interpolation): The interpolation to normalize.

    Returns:
        str: The formatted string representation of the interpolation.
    """
    converted = convert(intp.value, intp.conversion)
    return format(converted, intp.format_spec)


def normalize(intp: Interpolation) -> str | object:
    """
    Normalizes a PEP 750 Interpolation, preserving its type when possible.

    This is a more flexible version of normalize_str() that preserves the original
    value's type when no conversion is specified.

    If neither a conversion nor a format spec is specified, the original value
    is returned without any modification, ensuring that the value's type is preserved.

    Args:
        interpolation (Interpolation): The interpolation to normalize.

    Returns:
        str | object: The normalized string if conversion or format spec is specified, otherwise
            the original value.
    """
    if intp.conversion or intp.format_spec:
        return normalize_str(intp)
    else:
        return intp.value


@typing.overload
def bind(
    template: Template,
    binder: typing.Callable[[Interpolation], str],
    *,
    joiner: typing.Callable[[typing.Iterable[str]], str] = ...,
) -> str: ...
@typing.overload
def bind(
    template: Template,
    binder: typing.Callable[[Interpolation], str],
    *,
    joiner: typing.Callable[[typing.Iterable[str]], U],
) -> U: ...
@typing.overload
def bind(
    template: Template,
    binder: typing.Callable[[Interpolation], T],
    *,
    joiner: typing.Callable[[typing.Iterable[T | str]], U],
) -> U: ...
def bind(template: Template, binder, *, joiner="".join) -> typing.Any:
    """
    Binds a template by processing its interpolations using a binder function
    and combining the results with a joiner function.

    This function processes each `Interpolation` in the given template using the
    provided `binder` function, and then combines the processed parts using the
    `joiner` function. By default, the `joiner` concatenates the parts into a single
    string.

    Args:
        template (Template): A template to process.
        binder: A callable that transforms each Interpolation.
        joiner: A callable to join the processed template parts.
    """
    if not isinstance(template, Template):
        raise TypeError(f"Expected Template, got {type(template).__name__}")
    return joiner(_bind_iterator(template, binder))


@typing.overload
def binder(
    binder: typing.Callable[[Interpolation], str],
    joiner: typing.Callable[[typing.Iterable[str]], str] = ...,
) -> typing.Callable[[Template], str]: ...
@typing.overload
def binder(
    binder: typing.Callable[[Interpolation], str],
    joiner: typing.Callable[[typing.Iterable[str]], U],
) -> typing.Callable[[Template], U]: ...
@typing.overload
def binder(
    binder: typing.Callable[[Interpolation], T],
    joiner: typing.Callable[[typing.Iterable[T | str]], U],
) -> typing.Callable[[Template], U]: ...
def binder(binder, joiner="".join) -> typing.Any:
    """
    Creates a reusable template processor function from a binder function.

    This is a higher-order function that creates specialized template processors,
    as described in the "Creating Reusable Binders" section of PEP 750.
    Use this when you want to process multiple templates with the same transformation.

    Additionally, this can be used as a decorator to create reusable template
    processors in a concise and readable way.

    Args:
        binder: A function that transforms Interpolation objects.
        joiner: A function to join the processed template parts. Defaults to "".join.

    Returns:
        Callable[[Template], Any]: A function that processes templates using the given binder.

    Example:
        ```python
        @binder
        def html_render(interpolation: Interpolation) -> str:
            # Example binder that escapes HTML in interpolations
            return escape(normalize_str(interpolation))

        username = "<script>alert('XSS')</script>"
        template = t"Hello {username}!"
        result = html_render(template)
        assert result == "Hello &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;!"
        ```
    """
    return lambda template: bind(template, binder, joiner=joiner)


f = render = binder(normalize_str)
"""
Renders a template as a string, just like f-strings.

Args:
    template (Template): The template to render.

Returns:
    str: The rendered string.
"""


def template_eq(
    template1: Template,
    template2: Template,
    /,
    *,
    compare_value: bool = True,
    compare_expr: bool = True,
) -> bool:
    """
    Compares two Template objects for equivalence.

    This function checks whether two Template instances are equivalent by comparing
    their string and interpolation parts.

    Args:
        template1 (Template): The first template to compare.
        template2 (Template): The second template to compare.
        compare_value (bool, optional): If False, the 'value' attribute of each interpolation is not compared. Defaults to True.
        compare_expr (bool, optional): If False, the 'expression' attribute of each interpolation is not compared. Defaults to True.

    Returns:
        bool: True if the templates are considered equivalent based on the specified criteria, False otherwise.

    Example:
        ```python
        name = "world"
        template1 = t"Hello {name}!"
        template2 = t"Hello {name}!"
        assert template_eq(template1, template2)

        # Compare structure but not values
        name1 = "world"
        name2 = "universe"
        template1 = t"Hello {name1}!"
        template2 = t"Hello {name2}!"
        assert template_eq(template1, template2, compare_value=False)
        assert not template_eq(template1, template2, compare_value=True)
        ```
    """
    # Comparing strings also guarantees that the number of interpolations is equal.
    if template1.strings != template2.strings:
        return False
    for i1, i2 in zip(template1.interpolations, template2.interpolations, strict=True):
        if (
            i1.conversion != i2.conversion
            or i1.format_spec != i2.format_spec
            or compare_expr and i1.expression != i2.expression
            or compare_value and i1.value != i2.value
        ):
            return False
    return True


def _bind_iterator(template: Template, binder):
    for item in template:
        if isinstance(item, str):
            yield item
        else:
            yield binder(item)


def generate_template(
    string: typing.LiteralString,
    context: typing.Mapping[str, object] | None = None,
    /,
    *,
    globals: dict | None = None,
    use_eval: bool | None = None,
) -> Template:
    """
    Constructs a Template object from a string and a context.

    This function allows you to create Template objects dynamically at runtime by parsing a string,
    evaluating expressions found in the string against the provided context, and building a Template object.
    This is particularly useful in older Python versions that don't support t-string syntax.

    If both `context` and `globals` are not provided, this function automatically uses the parent function's
    local and global variables as `context` and `globals`, respectively. In this case, `use_eval` is set to True,
    so if the value inside the interpolation is not a simple variable but a more complex expression, it will be
    evaluated using `eval()`.

    If either `context` or `globals` is provided, `use_eval` is set to False by default. This means that if the
    interpolation contains anything other than a simple variable, a `TemplateGenerationError` will be raised.

    You can freely change this default behavior by adjusting the value of `use_eval`.

    If you want to access variables from a nonlocal scope, you need to declare them with
    the `nonlocal variable` statement in your function before using them in the template.

    Args:
        string (LiteralString): A string containing template to be parsed.
        context (Mapping): A mapping of variable names to values that
            will be used to evaluate expressions in the string. This parameter
            functions similarly to the locals parameter in Python's eval function.
        globals (dict, optional): Global variables to use for expression evaluation.
        use_eval (bool, optional): If True, expressions that aren't simple variable names
            will be evaluated using Python's eval function. If False, expressions must be
            simple variable names in the context dictionary. Defaults to False if context
            or globals is provided, otherwise defaults to True.

    Returns:
        Template: A Template object constructed from the parsed string.

    Raises:
        TemplateGenerationError: If use_eval=False and a variable cannot be found in the context.

    Example:
        ```python
        name = "world"
        template = generate_template("Hello {name}!")
        assert f(template) == "Hello world!"

        # With explicit context
        context = {"name": "universe"}
        template = generate_template("Hello {name}!", context)
        assert f(template) == "Hello universe!"

        # With expression evaluation
        context = {"x": 10, "y": 5}
        template = generate_template("Result: {x + y}", context, use_eval=True)
        assert f(template) == "Result: 15"
        ```
    """
    if context is None or globals is None:
        if use_eval is None:
            use_eval = True
        if (frame := inspect.currentframe()) and (parent_frame := frame.f_back):
            if context is None:
                context = parent_frame.f_locals
            if globals is None:
                globals = parent_frame.f_globals
        else:
            if context is None:
                context = {}
            if globals is None:
                globals = {}
    elif use_eval is None:
        use_eval = False

    parts = []
    for value, expr, format_spec, conv in _formatter.parse(string):
        parts.append(value)
        if expr is not None:
            try:
                value = context[expr]
            except Exception:
                no_key = True
            else:
                no_key = False
            if no_key:
                if use_eval:
                    value = eval(expr, globals, context)
                else:
                    raise TemplateGenerationError(f"'{expr}' is not defined or expression.")
            parts.append(Interpolation(value, expr, conv, format_spec))  # type: ignore
    return Template(*parts)  # type: ignore


t = generate_template


class _FrameVariables:
    """
    A class for accessing variables from the current frame and its parent frames (ancestors).

    This class allows retrieving both local and non-local variables by traversing up the stack frame hierarchy,
    enabling access to variables that are defined in parent scopes.
    """

    def __init__(self, frame: types.FrameType) -> None:
        self._first_frame = frame
        self._current_frame = frame
        self._variables = frame.f_locals
        self._reach_end = False
        self.shallow_getitem = True

    def __getitem__(self, key: str) -> object:
        try:
            return self._variables[key]
        except KeyError:
            if self._reach_end or self.shallow_getitem:
                raise

        self._retrieve_parent_frame()
        return self[key]

    def _retrieve_parent_frame(self) -> None:
        parent_frame = self._current_frame.f_back
        if parent_frame is None:
            self._reach_end = True
            return
        self._current_frame = parent_frame
        self._variables.update(parent_frame.f_locals)
