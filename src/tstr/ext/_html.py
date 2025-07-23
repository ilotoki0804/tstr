from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    import json
    from html import escape
else:
    json = escape = None

from tstr import Interpolation, binder, convert

__all__ = ["render_html", "Attribute"]


class Attribute(dict):
    """HTML attributes dictionary"""


@binder
def render_html(interp: Interpolation) -> str:
    """
    Escapes HTML special characters in interpolations for safe HTML rendering.

    The function supports the following format specifiers:
     - (empty): Regular HTML escaping for string values
     - `raw`: Allows raw HTML strings to be included without escaping. Accepts string
     - `json`: Converts any value to JSON and inserts it. Accepts any JSON-serializable value
     - `attrs`: Converts a dictionary to HTML attributes, escaping values appropriately. Accepts mappings

    Args:
        template (Template): The template to process.

    Returns:
        str: The HTML-escaped string based on format specifier rules

    Raises:
        ValueError or TypeError: If an invalid format specifier is used or if types don't match requirements

    Examples:
        ```python
        from tstr.ext import render_html, Attribute

        # Basic HTML escaping
        username = "<script>alert('XSS')</script>"
        result = render_html(t"<div>Welcome, {username}!</div>")
        # Result: "<div>Welcome, &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;!</div>"

        # Including raw HTML
        title_html = "<b>Important Notice</b>"
        result = render_html(t"<h1>{title_html:raw}</h1>")
        # Result: "<h1><b>Important Notice</b></h1>"

        # Converting to JSON
        data = {"name": "John", "age": 30}
        result = render_html(t"<script>const user = {data:json};</script>")
        # Result: '<script>const user = {"name": "John", "age": 30};</script>'

        # HTML attributes from dictionary
        attributes = {"src": "/image.jpg", "alt": "Profile picture", "data_index": 1}
        result = render_html(t"<img {attributes:attrs} />")
        # Result: '<img src="/image.jpg" alt="Profile picture" data-index="1" />'

        # HTML attributes with Attribute class
        result = render_html(t"<img {Attribute(src="/image.jpg", alt="Profile picture", data_index=1)} />")
        ```
    """
    global escape, json
    if escape is None:
        import json
        from html import escape

    match interp.format_spec, convert(interp.value, interp.conversion):
        case "", str(value):
            return escape(value)
        case "raw", str(value):
            return value
        case "json", value:
            return json.dumps(value)
        case (_, Attribute() as value) | ("attrs" | "attr", value):
            return " ".join(
                f'{attr.replace("_", "-")}="{escape(value)}"'
                for attr, value in value.items()  # type: ignore
            )
        case "", value:
            raise TypeError(
                f"Invalid value type '{type(value).__name__}' for HTML escaping. ")
        case "raw", value:
            raise TypeError(
                f"'raw' conversion is only allowed for strings. Value type: '{type(value).__name__}'")
        case _:
            raise ValueError(
                "Only 'raw', 'json', and 'attrs' are allowed for a format spec.")
