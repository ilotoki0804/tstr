from __future__ import annotations

import inspect
import types
import typing
from itertools import zip_longest  # type: ignore # I have no idea why this line cause errors in Pyright, but it's probably fine.
from string import Formatter

from ._interpolation_tools import normalize_str
from ._template import Interpolation, Template

__all__ = [
    "bind",
    "binder",
    "f",
    "render",
    "generate_template",
    "template_eq",
    "template_from_parts",
    "dedent",
]

_formatter = Formatter()
T = typing.TypeVar("T")
U = typing.TypeVar("U")


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

    Returns:
        The result of applying the joiner to the processed template parts.
    """
    if not isinstance(template, Template):
        raise TypeError(f"Expected Template, got {type(template).__name__}")
    return joiner(_bind_iterator(template, binder))


def _bind_iterator(template: Template, binder):
    for item in template:
        if isinstance(item, str):
            yield item
        else:
            yield binder(item)


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
        def render_html(interpolation: Interpolation) -> str:
            # Example binder that escapes HTML in interpolations
            return escape(normalize_str(interpolation))

        username = "<script>alert('XSS')</script>"
        template = t"Hello {username}!"
        result = render_html(template)
        assert result == "Hello &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;!"
        ```
    """
    return lambda template: bind(template, binder, joiner=joiner)


def render(template: Template) -> str:
    """
    Renders a template as a string, just like f-strings (alias: f).

    Args:
        template (Template): The template to render.

    Returns:
        str: The rendered string.
    """
    return bind(template, normalize_str)


f = render


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


def generate_template(
    string: typing.LiteralString | str,  # LiteralString is ineffective for static type checking here
    context: typing.Mapping[str, object] | None = None,
    *,
    globals: dict | None = None,
    use_eval: bool | None = None,
    frame: types.FrameType | None = None,
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
    interpolation contains anything other than a simple variable, a `KeyError` will be raised.
    The reason `KeyError` is raised is because `str.format()` also raises the same error.

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
        frame (FrameType, optional): Explicitly specify which stack frame to use for retrieving
            local and global variables when context or globals are not provided. By default,
            uses the caller's frame.


    Returns:
        Template: A Template object constructed from the parsed string.

    Raises:
        KeyError: If use_eval=False and a variable cannot be found in the context.

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
    if use_eval is None:
        use_eval = context is None and globals is None

    if context is None or globals is None:
        if frame or (current_frame := inspect.currentframe()) and (frame := current_frame.f_back):
            if context is None:
                context = frame.f_locals
            if globals is None:
                globals = frame.f_globals
        else:
            if context is None:
                context = {}
            if globals is None:
                globals = {}

    parts = []
    for literal, expr, format_spec, conv in _formatter.parse(string):
        parts.append(literal)
        if expr is not None:
            try:
                value = context[expr]
            except Exception:
                no_key = True
                # try:
                #     value = f"{{{expr}}}".format_map(context)
                # except Exception:
                #     no_key = True
                # else:
                #     no_key = False
            else:
                no_key = False
            if no_key:
                if use_eval:
                    value = eval(expr, globals, context)
                else:
                    raise KeyError(expr)
            parts.append(Interpolation(value, expr, conv, format_spec or ""))  # type: ignore
    return Template(*parts)


t = generate_template


def template_from_parts(strings: typing.Sequence[str], interpolations: typing.Sequence[Interpolation], strict=True) -> Template:
    """
    Constructs a Template object from component parts.

    This function creates a Template by interleaving strings and interpolations
    in alternating order. It's useful for reconstructing templates from their
    component parts.

    Args:
        strings: A sequence of string literals that form the static parts of the template.
        interpolations: A sequence of Interpolation objects that form the dynamic parts.
        strict (bool, optional): Controls validation of input length relationships.
            If True (default), enforces that the number of strings must be exactly one more
            than the number of interpolations.
            This ensures the standard template structure where strings and interpolations
            alternate, starting and ending with a string. This is the expected format
            for most template operations.
            If False, allows flexible input lengths where extra strings or interpolations
            are handled gracefully, useful for dynamic template construction scenarios.
            Defaults to True.

    Returns:
        Template: A Template object constructed from the provided strings and interpolations.

    Raises:
        ValueError: If strict=True and the number of strings is not exactly one more than
            the number of interpolations.
    """
    if strict and len(strings) != len(interpolations) + 1:
        raise ValueError(
            "The number of strings must be one more than the number of interpolations."
        )
    parts = []
    for string, interpolation in zip_longest(strings, interpolations):
        if string is not None:
            parts.append(string)
        if interpolation is not None:
            parts.append(interpolation)
    return Template(*parts)


def dedent(template: Template) -> Template:
    """
    Removes common leading whitespace from all lines in a template.

    This function is similar to textwrap.dedent() but works with Template objects,
    preserving interpolations while removing the common indentation from string parts.
    It analyzes all non-whitespace lines to determine the common leading whitespace
    and removes it from each line.

    The function handles template-specific considerations:
    - Lines immediately following interpolations are treated specially
    - Empty lines and whitespace-only lines are handled appropriately
    - The relative indentation between lines is preserved

    Args:
        template (Template): The template to dedent.

    Returns:
        Template: A new Template with common leading whitespace removed.

    Example:
        ```python
        name = "world"
        template = generate_template('''    Hello {name}!
            How are you?''')
        dedented = dedent(template)
        assert f(dedented) == "Hello world!\\n    How are you?"
        ```
    """
    # import textwrap; textwrap.dedent("")
    lines_list = [string.split("\n") for string in template.strings]
    effective_lines = [
        line
        for i, lines in enumerate(lines_list)
        for j, line in enumerate(lines)
        if
        # For better understanding, this evaluates cases where lines are 'excluded' and negates them
        not (
            # The first line of each lines group is excluded because it comes right after an interpolation.
            # However, the first line of lines_list is not excluded since it doesn't follow an interpolation.
            (j == 0 and i != 0)
            or (
                # Empty lines or lines consisting only of spaces are excluded
                (not line or line.isspace())
                # However, even if a line is empty or consists only of spaces,
                # the last line of each lines group is not excluded because it comes right before an interpolation.
                # However, the last line of lines_list is excluded since it doesn't precede an interpolation.
                and (j + 1 != len(lines) or i + 1 == len(lines_list))
            )
        )
    ]
    # If line1 consists only of whitespace, margin might be evaluated as one less
    # Therefore, add one more non-whitespace character at the end of the line
    line1 = min(effective_lines, default="") + "\0"
    line2 = max(effective_lines, default="") + "\0"
    margin = 0
    for margin, char in enumerate(line1):
        if char != line2[margin] or char not in " \t":
            break
    strings = [
        "\n".join(
            line[margin:]
            # Same logic as above
            if not (
                (j == 0 and i != 0)
                or (not line or line.isspace())
                and (j + 1 != len(lines) or i + 1 == len(lines_list))
            )
            # Clear all whitespace from whitespace-only lines, like textwrap.dedent()
            else "" if line.isspace() else line
            for j, line in enumerate(lines)
        )
        for i, lines in enumerate(lines_list)
    ]
    return template_from_parts(strings, template.interpolations)
