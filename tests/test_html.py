# type: ignore

from __future__ import annotations

import pytest

from tstr import t
from tstr.ext._html import Attribute, render_html


def test_render_html_invalid_type():
    with pytest.raises(TypeError):
        render_html(42)

    with pytest.raises(TypeError):
        render_html("Hello, World!")


def test_render_html_escapes_html():
    username = "<script>alert('XSS')</script>"
    template = t("Hello, {username}!")
    result = render_html(template)
    assert result == "Hello, &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;!"


def test_render_html_raw_html():
    raw_html = "<b>BOLD TITLE</b>"
    template = t("<h1>{raw_html:raw}</h1>")
    result = render_html(template)
    assert result == "<h1><b>BOLD TITLE</b></h1>"


def test_render_html_json():
    template = t("<script>{dict(data=123):json}.data</script>")
    result = render_html(template)
    assert result == '<script>{"data": 123}.data</script>'


def test_render_html_attrs():
    template = t("<img {dict(src='image.jpg', alt='I like t-strings', data_hello='world'):attrs} />")
    result = render_html(template)
    assert result == '<img src="image.jpg" alt="I like t-strings" data-hello="world" />'


def test_render_html_attrs_with_class():
    _ = Attribute()  # to inform linters that Attribute() is used.
    template = t('<img {Attribute(src="/image.jpg", alt="Profile picture", data_index="1")} />')
    result = render_html(template)
    assert result == '<img src="/image.jpg" alt="Profile picture" data-index="1" />'


def test_render_html_with_conversion():
    val = 42
    template = t("value: {val!s}")
    assert render_html(template) == "value: 42"

    val = "value"
    template = t("value: {val!r}")
    assert render_html(template) == "value: &#x27;value&#x27;"

    val = "value"
    template = t("value: {val!r:raw}")
    assert render_html(template) == "value: 'value'"

    val = "안녕"
    template = t("value: {val!a}")
    assert render_html(template) == "value: &#x27;\\uc548\\ub155&#x27;"


def test_render_html_raises_on_invalid_type():
    val = 42
    template = t("{val}")
    with pytest.raises(TypeError):
        render_html(template)

    template = t("{val:raw}")
    with pytest.raises(TypeError):
        render_html(template)

    template = t("{val:attrs}")
    with pytest.raises(AttributeError):
        render_html(template)
