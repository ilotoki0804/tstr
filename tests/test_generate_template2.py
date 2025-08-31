# type: ignore
# source: Lib/test/test_tstring.py

from __future__ import annotations

from unittest.mock import patch

from _support import TStringTestCase
import tstr._compat as compat
from tstr import generate_template, f as fstring, t


class TestTString(TStringTestCase):
    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_string_representation(self):
        # Test __repr__
        t = generate_template("Hello")
        self.assertEqual(repr(t), "Template(strings=('Hello',), interpolations=())")

        name = "Python"
        t = generate_template("Hello, {name}")
        self.assertEqual(
            repr(t),
            "Template(strings=('Hello, ', ''), "
            "interpolations=(Interpolation('Python', 'name', None, ''),))",
        )

    # @patch("tstr._utils.Template", compat.Template)
    # @patch("tstr._utils.Interpolation", compat.Interpolation)
    def test_generate_template_flags(self):
        assert type(self) is __class__
        assert __class__.__name__ == "TestTString"
        name = "Python"
        t = generate_template("hello, {name}")
        self.assertTStringEqual(t, ("hello, ", ""), [(name, "name")])

        raises = self.assertRaises
        t_string_eq = self.assertTStringEqual

        with raises(NameError):
            generate_template("hello, {name} {world}")

        with raises(KeyError):
            generate_template("hello, {name} {world}", use_eval=False)

        with raises(KeyError):
            generate_template("hello, {name} {1 + 2}", use_eval=False)

        with raises(KeyError):
            generate_template("hello, {name + 1}", use_eval=False)

        with raises(KeyError):
            generate_template("hello, {name + 1}", use_eval=False)

        # def func():
        #     world = "world"
        #     return generate_template("hello, {name} {world}", include_nonlocals=True)
        # t_string_eq(func(), ("hello, ", " ", ""), [(name, "name"), ("world", "world")])

        # def func():
        #     return generate_template("hello, {name}", include_nonlocals=False)
        # with raises(NameError):
        #     func()

        # def func():
        #     return generate_template("hello, {name}", include_nonlocals=False, use_eval=False)
        # with raises(KeyError):
        #     func()

        # def func():
        #     world = "world"
        #     return generate_template("hello, {name} {world}", include_nonlocals=True, use_eval=False)
        # t_string_eq(func(), ("hello, ", " ", ""), [(name, "name"), ("world", "world")])

        def func():
            nonlocal name
            world = "world"
            return generate_template("hello, {name} {world}")
        t_string_eq(func(), ("hello, ", " ", ""), [(name, "name"), ("world", "world")])

        t = generate_template("hello, {hello}", dict(hello="world"), use_eval=False)
        t_string_eq(t, ("hello, ", ""), [("world", "hello")])

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_interpolation_basics(self):
        # Test basic interpolation
        name = "Python"
        t = generate_template("Hello, {name}")
        self.assertTStringEqual(t, ("Hello, ", ""), [(name, "name")])
        self.assertEqual(fstring(t), "Hello, Python")

        # Multiple interpolations
        first = "Python"
        last = "Developer"
        t = generate_template("{first} {last}")
        self.assertTStringEqual(t, ("", " ", ""), [(first, "first"), (last, "last")])
        self.assertEqual(fstring(t), "Python Developer")

        # Interpolation with expressions
        a = 10
        b = 20
        t = generate_template("Sum: {a + b}")
        self.assertTStringEqual(t, ("Sum: ", ""), [(a + b, "a + b")])
        self.assertEqual(fstring(t), "Sum: 30")

        # Interpolation with function
        def square(x):
            return x * x

        t = generate_template("Square: {square(5)}")
        self.assertTStringEqual(t, ("Square: ", ""), [(square(5), "square(5)")])
        self.assertEqual(fstring(t), "Square: 25")

        # Test attribute access in expressions
        class Person:
            def __init__(self, name):
                self.name = name

            def upper(self):
                return self.name.upper()

        person = Person("Alice")
        t = generate_template("Name: {person.name}")
        self.assertTStringEqual(t, ("Name: ", ""), [(person.name, "person.name")])
        self.assertEqual(fstring(t), "Name: Alice")

        # Test method calls
        t = generate_template("Name: {person.upper()}")
        self.assertTStringEqual(t, ("Name: ", ""), [(person.upper(), "person.upper()")])
        self.assertEqual(fstring(t), "Name: ALICE")

        # Test dictionary access
        data = {"name": "Bob", "age": 30}
        t = generate_template("Name: {data['name']}, Age: {data['age']}")
        self.assertTStringEqual(
            t,
            ("Name: ", ", Age: ", ""),
            [(data["name"], "data['name']"), (data["age"], "data['age']")],
        )
        self.assertEqual(fstring(t), "Name: Bob, Age: 30")

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_format_specifiers(self):
        # Test basic format specifiers
        value = 3.14159
        t = generate_template("Pi: {value:.2f}")
        self.assertTStringEqual(t, ("Pi: ", ""), [(value, "value", None, ".2f")])
        self.assertEqual(fstring(t), "Pi: 3.14")

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_conversions(self):
        # Test !s conversion (str)
        obj = object()
        t = generate_template("Object: {obj!s}")
        self.assertTStringEqual(t, ("Object: ", ""), [(obj, "obj", "s")])
        self.assertEqual(fstring(t), f"Object: {str(obj)}")

        # Test !r conversion (repr)
        t = generate_template("Data: {obj!r}")
        self.assertTStringEqual(t, ("Data: ", ""), [(obj, "obj", "r")])
        self.assertEqual(fstring(t), f"Data: {repr(obj)}")

        # Test !a conversion (ascii)
        text = "Café"
        t = generate_template("ASCII: {text!a}")
        self.assertTStringEqual(t, ("ASCII: ", ""), [(text, "text", "a")])
        self.assertEqual(fstring(t), f"ASCII: {ascii(text)}")

        # Test !z conversion (error)
        # generate_template raises ValueError instead of SyntaxError
        num = 1
        with self.assertRaises(ValueError):
            eval("generate_template('{num!z}')")

    # debug specifier is not supported in generate_template
    # def test_debug_specifier(self):
    #     # Test debug specifier
    #     value = 42
    #     t = generate_template("Value: {value=}")
    #     self.assertTStringEqual(
    #         t, ("Value: value=", ""), [(value, "value", "r")]
    #     )
    #     self.assertEqual(fstring(t), "Value: value=42")

    #     # Test debug specifier with format (conversion default to !r)
    #     t = generate_template("Value: {value=:.2f}")
    #     self.assertTStringEqual(
    #         t, ("Value: value=", ""), [(value, "value", None, ".2f")]
    #     )
    #     self.assertEqual(fstring(t), "Value: value=42.00")

    #     # Test debug specifier with conversion
    #     t = generate_template("Value: {value=!s}")
    #     self.assertTStringEqual(
    #         t, ("Value: value=", ""), [(value, "value", "s")]
    #     )

    #     # Test white space in debug specifier
    #     t = generate_template("Value: {value = }")
    #     self.assertTStringEqual(
    #         t, ("Value: value = ", ""), [(value, "value", "r")]
    #     )
    #     self.assertEqual(fstring(t), "Value: value = 42")

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_raw_tstrings(self):
        path = r"C:\Users"
        t = generate_template(r"{path}\Documents")
        self.assertTStringEqual(t, ("", r"\Documents"), [(path, "path")])
        self.assertEqual(fstring(t), r"C:\Users\Documents")

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_template_concatenation(self):
        # Test template + template
        t1 = t("Hello, ")
        t2 = t("world")
        combined = t1 + t2
        self.assertTStringEqual(combined, ("Hello, world",), ())
        self.assertEqual(fstring(combined), "Hello, world")

        # Test template + string
        t1 = t("Hello")
        expected_msg = 'can only concatenate tstr.Template ' \
            '\\(not "str"\\) to tstr.Template'
        with self.assertRaisesRegex(TypeError, expected_msg):
            t1 + ", world"

        # Test template + template with interpolation
        name = "Python"
        t1 = t("Hello, ")
        t2 = t("{name}")
        combined = t1 + t2
        self.assertTStringEqual(combined, ("Hello, ", ""), [(name, "name")])
        self.assertEqual(fstring(combined), "Hello, Python")

        # Test string + template
        expected_msg = 'can only concatenate str ' \
            '\\(not "tstr.Template"\\) to str'
        with self.assertRaisesRegex(TypeError, expected_msg):
            "Hello, " + t("{name}")

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_nested_templates(self):
        # Test a template inside another template expression
        name = "Python"
        inner = generate_template("{name}")
        t = generate_template("Language: {inner}")

        t_interp = t.interpolations[0]
        self.assertEqual(t.strings, ("Language: ", ""))
        self.assertEqual(t_interp.value.strings, ("", ""))
        self.assertEqual(t_interp.value.interpolations[0].value, name)
        self.assertEqual(t_interp.value.interpolations[0].expression, "name")
        self.assertEqual(t_interp.value.interpolations[0].conversion, None)
        self.assertEqual(t_interp.value.interpolations[0].format_spec, "")
        self.assertEqual(t_interp.expression, "inner")
        self.assertEqual(t_interp.conversion, None)
        self.assertEqual(t_interp.format_spec, "")

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_syntax_errors(self):
        x = 42
        for case, _ in (
            # ("generate_template(')", "unterminated t-string literal"),
            # ("generate_template(''')", "unterminated triple-quoted t-string literal"),
            # ("generate_template('''')", "unterminated triple-quoted t-string literal"),
            # ("generate_template('{)", "'{' was never closed"),
            (
                "generate_template('{')",
                "Single '{' encountered in format string",
            ),
            ("generate_template('{a')", "expected '}' before end of string"),
            ("generate_template('}')", "Single '}' encountered in format string"),
            ("generate_template('{}')", "t-string: valid expression required before '}'"),
            ("generate_template('{=x}')", "t-string: valid expression required before '='"),
            ("generate_template('{!x}')", "t-string: valid expression required before '!'"),
            ("generate_template('{:x}')", "t-string: valid expression required before ':'"),
            ("generate_template('{x;y}')", "t-string: expecting '=', or '!', or ':', or '}'"),
            ("generate_template('{x=y}')", "t-string: expecting '!', or ':', or '}'"),
            ("generate_template('{x!s!}')", "t-string: expecting ':' or '}'"),
            ("generate_template('{x!s:')", "t-string: expecting '}', or format specs"),
            ("generate_template('{x!}')", "t-string: missing conversion character"),
            ("generate_template('{x=!}')", "t-string: missing conversion character"),
            ("generate_template('{x!z}')", "t-string: invalid conversion character 'z': "
                         "expected 's', 'r', or 'a'"),
            ("generate_template('{lambda:1}')", "t-string: lambda expressions are not allowed "
                              "without parentheses"),
            # ("generate_template('{x:{;}}')", "t-string: expecting a valid expression after '{'"),
        ):
            with self.subTest(case), self.assertRaisesRegex((ValueError, SyntaxError), '.*'):
                eval(case)

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_runtime_errors(self):
        # Test missing variables
        with self.assertRaises(NameError):
            eval("generate_template('Hello, {name}')")

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_triple_quoted(self):
        # Test triple-quoted t-strings
        t = generate_template(
            """
        Hello,
        world
        """,
            locals(),
        )
        self.assertTStringEqual(t, ("\n        Hello,\n        world\n        ",), ())
        self.assertEqual(fstring(t), "\n        Hello,\n        world\n        ")

        # Test triple-quoted with interpolation
        name = "Python"
        t = generate_template(
            """
        Hello,
        {name}
        """,
            locals(),
        )
        self.assertTStringEqual(
            t, ("\n        Hello,\n        ", "\n        "), [(name, "name")]
        )
        self.assertEqual(fstring(t), "\n        Hello,\n        Python\n        ")
