# tstr - PEP 750 Template String Utilities & Backports

[![PyPI Version](https://img.shields.io/pypi/v/tstr)](https://pypi.org/project/tstr/)
[![Python Version](https://img.shields.io/pypi/pyversions/tstr)](https://pypi.org/project/tstr/)
[![License](https://img.shields.io/github/license/ilotoki0804/tstr)](https://github.com/ilotoki0804/tstr/blob/master/LICENSE)
[![Tests](https://github.com/ilotoki0804/tstr/workflows/testing/badge.svg)](https://github.com/ilotoki0804/tstr/actions)
[![Coverage Status](https://coveralls.io/repos/github/ilotoki0804/tstr/badge.svg?branch=main)](https://coveralls.io/github/ilotoki0804/tstr?branch=main)

`tstr` provides utilities for working with [PEP 750 template strings](https://peps.python.org/pep-0750/), along with robust backports for older Python versions.

This library streamlines template string usage by offering practical helpers and common processing patterns. For Python versions prior to 3.14, `tstr` seamlessly backports template string functionality.

## Installation

Install `tstr` via pip:

```bash
pip install tstr
```

## Features

- `render` (alias: `f`): Render a template to a string, mimicking f-string behavior.
- `generate_template` (alias: `t`): Create a Template object from a string and context.
    This function is especially useful on Python versions that do not support template strings natively.
- `bind`: Apply a function to all interpolations in a template.
- `binder`: Decorator to create template processors from an interpolation processor.
- `normalize`: Convert an interpolation to its value, preserving type when possible.
- `normalize_str`: Convert an interpolation to a string.
- `convert`: Apply f-string-style conversion to a value.
- `template_eq`: Check if two templates are equivalent.

Experimental applications:

- `render_html`: Render templates with HTML escaping.
- `execute`: Safely execute SQL with templates, preventing injection.
- `TemplateFormatter`: Enable Python's logging module to accept template strings.

Below are usage examples for each function. For more details, see the [API documentation](/docs/api.md).

```python
from tstr import Template, Interpolation, generate_template, render, bind, binder, f, normalize, normalize_str, convert, template_eq

# Rendering templates
x = 12
template = t"Value: {x}"
print(render(template))  # "Value: 12"
print(f(template))  # "Value: 12"

# Generating templates
template = generate_template("Hello, {name}!", {"name": "Alice"})  # with explicit context
print(f(template))  # "Hello, Alice!"

name = "Bob"
template = generate_template("Nice to meet you, {name}!")  # without explicit context
print(f(template))  # "Nice to meet you, Bob!"

template = t("Nice to meet you, {name}!")  # with an alias `t`
print(f(template))  # "Nice to meet you, Bob!"

# Binding all interpolations
def double(i: Interpolation):
    return str(i.value * 2)
n = 10
template = t"Double: {n}"
print(bind(template, double))  # "Double: 20"

@binder
def upper(i):
    return normalize_str(i).upper()
name = 'bob'
template = t"Hi, {name}!"
print(upper(template))  # "Hi, BOB!"

# Applying conversion and formatting
age = 20
template = t"Age: {age:04d}"
intp = template.interpolations[0]
print(normalize(intp))  # "0020"

# Applying conversion
print(convert(42, "r"))  # e.g., "42"

# Template equivalence
x = 123
t1 = t"A: {x}"
t2 = t"A: {x}"
print(template_eq(t1, t2))  # True
```

## Compatibility

`tstr` automatically detects native template string support (PEP 750):

- Python 3.14+: Uses native template strings.
- Python 3.10–3.13: Uses a compatible backport.

Use the `TEMPLATE_STRING_SUPPORTED` constant to check if template strings are natively supported in your Python version.

# Contributing

This project welcomes contributions of all kinds from anyone willing to help improve it! Whether you're fixing a typo in documentation, reporting a bug, proposing a new feature, or implementing code changes - every contribution matters and is highly appreciated.

## Releases

* 0.2.0: Rename html_render to render_html, add `_logging` module, fix various bugs and improve documentation
* 0.1.1.post1: Initial release

## License

Apache License 2.0
