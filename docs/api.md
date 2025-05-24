# tstr API Documentation

## Utility Functions

### Creating Templates

```python
from tstr import t, f, generate_template

# Create a template string literal
name = "world"
template = t"Hello, {name}!"
# Render the template
print(f(template))  # "Hello, world!"

# Programmatically create templates (for Python < 3.14)
template = generate_template("Hello, {name}!")
print(f(template))  # "Hello, world!"
# Or use t() as a function
template = t("Hello, {name}!")
print(f(template))  # "Hello, world!"
```

### Template Operations

```python
from tstr import t, f, normalize, normalize_str, template_eq

# Normalize interpolation values
age = 42
template = t"Hello, {age}!"
interp = template.interpolations[0]
print(normalize(interp))  # 42
print(normalize_str(interp))  # "42"

# Compare templates for equality
name = "Python"
t1 = t"Hello, {name}!"
t2 = t"Hello, {name}!"
assert template_eq(t1, t2)
```

### Custom Template Processors

```python
from tstr import t, binder, Interpolation

# Use binder to decorate a function that processes Interpolation values,
# turning it into a Template converter.
@binder
def uppercase_names(i: Interpolation) -> str:
    return normalize_str(i.value).upper()

name = "world"
template = t("Hello, {name}!")
print(uppercase_names(template))  # "Hello, WORLD!"
```

### interpolation_replace

Creates a new `Interpolation` by selectively replacing attributes of an existing one.

This function allows you to create a modified copy of an `Interpolation` object by specifying which attributes to replace. Any attribute not explicitly provided will retain its original value from the input interpolation.

#### Parameters

- `interp` (Interpolation): The original interpolation object.
- `value` (object, optional): New value to use instead of the original.
- `expression` (str, optional): New expression to use instead of the original.
- `conversion` (Literal["a", "r", "s"] | None, optional): New conversion to use.
- `format_spec` (str, optional): New format specification to use.

#### Returns

- `Interpolation`: A new Interpolation with the specified replacements.

#### Examples

```python
name = "world"
template = t"Hello {name:>10}!"
orig_interp = template.interpolations[0]

# Replace just the value
new_interp = interpolation_replace(orig_interp, value="universe")
assert new_interp.value == "universe"
assert new_interp.expression == orig_interp.expression
assert new_interp.format_spec == ">10"

# Replace the format specification
new_interp = interpolation_replace(orig_interp, format_spec="^20")
assert new_interp.value == "world"
assert new_interp.format_spec == "^20"

# Replace the conversion
new_interp = interpolation_replace(orig_interp, conversion="r")
assert new_interp.conversion == "r"
assert f(Template("", new_interp)) == "   'world'"

# Replace multiple attributes
new_interp = interpolation_replace(
    orig_interp,
    value=123,
    format_spec=".2f",
)
assert new_interp.value == 123
assert new_interp.format_spec == ".2f"
assert f(Template("", new_interp)) == "123.00"
```

## Experimental Applications

`tstr` offers experimental applications that showcase real-world uses for template strings:

### Safe HTML Rendering

Escape HTML special characters in template interpolations to prevent XSS attacks:

```python
from tstr._html import render_html

user_input = "<script>alert('XSS')</script>"
template = t"<div>{user_input}</div>"
assert render_html(template) == "<div>&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;</div>"
```

### SQL Injection Prevention

Safely execute SQL queries using template strings to guard against SQL injection:

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

### Template-Based Logging

Integrate t-strings with Python's logging system using `TemplateFormatter`, which enables template-based log messages with lazy evaluation of callable values:

```python
from tstr import t
from tstr._logging import TemplateFormatter, install, uninstall, logging_context
import logging

# Configure a logger with TemplateFormatter
logger = logging.getLogger("app")
handler = logging.StreamHandler()
handler.setFormatter(TemplateFormatter())
logger.addHandler(handler)

# Log with template strings
user = "admin"
logger.info(t"User {user} logged in")

# Lazy evaluation of expensive __str__ or __repr__
# The message is only built if this log level is enabled
logger.debug(t"Global variables: {globals()}")

# Install globally for all loggers
install()
logger_type = "any"
logging.info(t"This works for {logger_type} logger")
uninstall()

# Or use as a context manager
with logging_context():
    logging.warning(t"Temporary template logging")
```
