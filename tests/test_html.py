# type: ignore

from __future__ import annotations

import pytest
from tstr._html import html_render
from tstr import t, f


def test_html_render_escapes_html():
    username = "<script>alert('XSS')</script>"
    template = t("Hello, {username}!")
    result = html_render(template)
    assert result == "Hello, &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;!"


def test_html_render_allows_raw_html():
    raw_html = "<b>BOLD TITLE</b>"
    template = t("<h1>{raw_html:raw}</h1>")
    result = html_render(template)
    assert result == "<h1><b>BOLD TITLE</b></h1>"


def test_html_render_allows_json():
    template = t("<script>{dict(data=123):json}.data</script>")
    result = html_render(template)
    assert result == '<script>{"data": 123}.data</script>'


def test_html_render_allows_json():
    template = t("<img {dict(src='image.jpg', alt='I like t-strings', data_hello='world'):attrs} />")
    result = html_render(template)
    assert result == '<img src="image.jpg" alt="I like t-strings" data-hello="world" />'


def test_html_render_with_conversion():
    val = 42
    template = t("value: {val!s}")
    assert html_render(template) == "value: 42"

    val = "value"
    template = t("value: {val!r}")
    assert html_render(template) == "value: &#x27;value&#x27;"

    val = "value"
    template = t("value: {val!r:raw}")
    assert html_render(template) == "value: 'value'"

    val = "안녕"
    template = t("value: {val!a}")
    assert html_render(template) == "value: &#x27;\\uc548\\ub155&#x27;"


def test_html_render_raises_on_invalid_type():
    val = 42
    template = t("{val}")
    with pytest.raises(TypeError):
        html_render(template)

    template = t("{val:raw}")
    with pytest.raises(TypeError):
        html_render(template)

    template = t("{val:attrs}")
    with pytest.raises(AttributeError):
        html_render(template)
