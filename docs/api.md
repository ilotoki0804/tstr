# Package APIs

## Creating Templates

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

## Template Operations

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

## Custom Template Processors

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

## Experimental Applications

`tstr` offers experimental applications that showcase real-world uses for template strings:

## Safe HTML Rendering

Escape HTML special characters in template interpolations to prevent XSS attacks:

```python
from tstr._html import render_html

user_input = "<script>alert('XSS')</script>"
template = t"<div>{user_input}</div>"
assert render_html(template) == "<div>&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;</div>"
```

## SQL Injection Prevention

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

## Template-Based Logging

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
