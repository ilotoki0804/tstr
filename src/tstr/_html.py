from __future__ import annotations

from html import escape
import json

from tstr import Interpolation, binder
from tstr._utils import convert

__all__ = ["html_render"]


@binder
def html_render(intp: Interpolation) -> str:
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
        from tstr._html import html_render

        # Basic HTML escaping
        username = "<script>alert('XSS')</script>"
        result = html_render(t"<div>Welcome, {username}!</div>")
        # Result: "<div>Welcome, &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;!</div>"

        # Including raw HTML
        title_html = "<b>Important Notice</b>"
        result = html_render(t"<h1>{title_html:raw}</h1>")
        # Result: "<h1><b>Important Notice</b></h1>"

        # Converting to JSON
        data = {"name": "John", "age": 30}
        result = html_render(t"<script>const user = {data:json};</script>")
        # Result: '<script>const user = {"name": "John", "age": 30};</script>'

        # HTML attributes from dictionary
        attributes = {"src": "/image.jpg", "alt": "Profile picture", "data_index": 1}
        result = html_render(t"<img {attributes:attrs}>")
        # Result: '<img src="/image.jpg" alt="Profile picture" data-index="1">'
        ```
    """
    match intp.format_spec, convert(intp.value, intp.conversion):
        case "", str(value):
            return escape(value)
        case "raw", str(value):
            return value
        case "json", value:
            return json.dumps(value)
        case "attrs" | "attr", value:
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
