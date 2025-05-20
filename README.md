[![PyPI Version](https://img.shields.io/pypi/v/tstr)](https://pypi.org/project/tstr/)
[![Python Version](https://img.shields.io/pypi/pyversions/tstr)](https://pypi.org/project/tstr/)
[![License](https://img.shields.io/github/license/ilotoki0804/tstr)](https://github.com/ilotoki0804/tstr/blob/master/LICENSE)
[![Tests](https://github.com/ilotoki0804/tstr/workflows/testing/badge.svg)](https://github.com/ilotoki0804/tstr/actions)

Various template string utilities, with backports for older versions of Python.

`tstr` is a Python library that provides convenient utility functions for working with [PEP 750 template strings](https://peps.python.org/pep-0750/).
`tstr` makes template strings easier to use by providing common processing patterns and utilities.

For Python versions older than 3.14, `tstr` includes a backport allowing you to use template strings functionality in earlier Python versions.

## Installation

You can install the `tstr` package using pip:

```bash
pip install tstr
```

## Features

- Create and manipulate template strings programmatically
- Full compatibility with Python 3.14's template strings (PEP 750)
- Backport for Python 3.10-3.13
- Utility functions for binding, rendering, and comparing templates

## Installation

```bash
pip install tstr
```

## Included Functions

- `generate_template` (alias: `t`) - Construct a Template object from a string and context
- `render` (alias: `f`)- Render a template to a string, just like f-strings
- `bind` - Process a template's interpolations with a binder function
- `binder` - Create a reusable template processor function
- `normalize` - Convert an interpolation to its value, preserving type when possible
- `normalize_str` - Convert an interpolation to a string
- `convert` - Apply f-string-like conversion to a value
- `converter` - Get a callable that performs f-string conversion
- `template_eq` - Compare two templates for equivalence

The package includes the following experimental applications:

- `html_render` - Escape HTML with templates
- `execute` - Execute SQL with templates, preventing injection attacks

## Compatibility

The package automatically detects if native template strings (PEP 750) are supported in your Python version:

- Python 3.14+: Uses native template string
- Python 3.10-3.13: Uses compatible backport implementation

The package provides a boolean constant `TEMPLATE_STRING_SUPPORTED` to check if your Python version supports template strings.

## Usage

### Creating Templates

```python
from tstr import t, f, generate_template

# Create a template string literal
name = "world"
template = t"Hello, {name}!"
# and render it
print(f(template))  # "Hello, world!"

# Create templates programmatically (useful for Python < 3.14)
template = generate_template("Hello, {name}!")
print(f(template))  # "Hello, world!"
# or using t()
template = t("Hello, {name}!")
print(f(template))  # "Hello, world!"
```

### Template Operations

```python
from tstr import t, f, normalize, normalize_str, template_eq

# Normalize interpolations
age = 42
template = t"Hello, {age}!"
interp = template.interpolations[0]
print(normalize(interp))  # 42
print(normalize_str(interp))  # "42"

# Compare templates
name = "Python"
t1 = t("Hello, {name}!")
t2 = t("Hello, {name}!")
assert template_eq(t1, t2)
```

### Custom Template Processors

```python
from tstr import t, binder, Interpolation

# binder decorates a function that accepts Interpolation values
# and transforms it into a Template converter
@binder
def uppercase_names(i: Interpolation) -> str:
    return normalize_str(i.value).upper()

name = "world"
template = t("Hello, {name}!")
print(uppercase_names(template))  # "Hello, WORLD!"
```

## Experimental Applications

`tstr` includes several experimental applications that demonstrate how template strings can be applied in real-world scenarios:

### Safe HTML Rendering

Automatically escape HTML special characters in template interpolations to prevent XSS attacks:

```python
from tstr._html import html_render

user_input = "<script>alert('XSS')</script>"
template = t"<div>{user_input}</div>"
assert html_render(template) == "<div>&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;</div>"
```

### SQL Injection Prevention

Execute SQL queries with template strings while protecting against SQL injection:

```python
from tstr._sqlite import execute
import sqlite3

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute("CREATE TABLE users (id PRIMARY KEY, name STRING)")
cursor.execute("INSERT INTO users (name) VALUES ('hello')")

user_input = "'; DROP TABLE users; --"
assert execute(cursor, t"SELECT * FROM users WHERE name = {user_input}").fetchone() is None

cursor.close()
conn.close()
```

## License

Apache License 2.0
