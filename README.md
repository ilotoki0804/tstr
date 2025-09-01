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
- `bind`: Apply a function to all interpolations and join all the parts.
- `binder`: Decorator to create template processors from an interpolation processor.
- `normalize` / `normalize_str`: Apply conversion and format to value.
- `convert`: Apply conversion to a value.
- `template_eq`: Check if two templates are equivalent.
- `interpolation_replace`: Create a new `Interpolation` by selectively replacing attributes of an existing one.
- `dedent`: `textwrap.dedent` for template strings
- `template_from_parts`: Construct template strings from iterable

This library also provides several useful extensions where template strings can be effectively utilized.
These extensions are available in the `tstr.ext` submodule, and below is a list with brief descriptions:

- `ext._html`: Render templates with HTML escaping.
- `ext._sqlite`: Safely execute SQL with templates, preventing SQL injection attacks.
- `ext._logging`: Enable Python's logging module to accept template strings.

For more details, see the [API documentation](/docs/api.md).

## Compatibility

`tstr` automatically detects native template string support (PEP 750):

- Python 3.14+: Uses native template strings.
- Python 3.10–3.13: Uses a compatible backport.

Use the `TEMPLATE_STRING_SUPPORTED` constant to check if template strings are natively supported in your Python version.

For details on how the compatible backport of template string works and what similarities and differences it has with native template strings, see the [compatible template strings](/docs/compat.md) documentation.

# Contributing

This project welcomes contributions of all kinds from anyone willing to help improve it! Whether you're fixing a typo in documentation, reporting a bug, proposing a new feature, or implementing code changes - every contribution matters and is highly appreciated.

## Releases

* 0.3.0: Revamp various things
* 0.2.0: Rename html_render to render_html, add `_logging` module, fix various bugs and improve documentation
* 0.1.1.post1: Initial release

## License

This library is licensed under the Apache License 2.0.
