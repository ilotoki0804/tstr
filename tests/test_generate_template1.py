# type: ignore
# Source: cpython/Lib/test/test_string/test_tstr.py

from __future__ import annotations

import pickle
import unittest
from unittest.mock import patch
from collections.abc import Iterator, Iterable

import pytest

from _support import TStringTestCase, fstring
import tstr._compat as compat
from tstr import Interpolation, Template, Interpolation, generate_template, convert, t


class TestTemplate(TStringTestCase):
    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_common(self):
        self.assertEqual(type(generate_template("")).__name__, "Template")
        self.assertEqual(type(generate_template("")).__qualname__, "Template")
        self.assertEqual(
            type(generate_template("")).__module__, "tstr._compat"
        )

        a = "a"
        i = generate_template("{a}").interpolations[0]
        self.assertEqual(type(i).__name__, "Interpolation")
        self.assertEqual(type(i).__qualname__, "Interpolation")
        self.assertEqual(type(i).__module__, "tstr._compat")

    @pytest.mark.skip("No exception will be raised when subclassing compat.Template, but it's marked as final.")
    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_final_types(self):
        with self.assertRaisesRegex(TypeError, 'is not an acceptable base type'):
            class Sub(compat.Template): ...

        with self.assertRaisesRegex(TypeError, 'is not an acceptable base type'):
            class Sub(compat.Interpolation): ...
        pass

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_basic_creation(self):
        # Simple t-string creation
        t = generate_template("Hello, world")
        self.assertIsInstance(t, compat.Template)
        self.assertTStringEqual(t, ("Hello, world",), ())
        self.assertEqual(fstring(t), "Hello, world")

        # Empty t-string
        t = generate_template("")
        self.assertTStringEqual(t, ("",), ())
        self.assertEqual(fstring(t), "")

        # Multi-line t-string
        t = generate_template(
            """Hello,
world""",
            locals(),
        )
        self.assertEqual(t.strings, ("Hello,\nworld",))
        self.assertEqual(len(t.interpolations), 0)
        self.assertEqual(fstring(t), "Hello,\nworld")

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_creation_interleaving(self):
        # Should add strings on either side
        t = Template(Interpolation("Maria", "name", None, ""))
        self.assertTStringEqual(t, ("", ""), [("Maria", "name")])
        self.assertEqual(fstring(t), "Maria")

        # Should prepend empty string
        t = Template(Interpolation("Maria", "name", None, ""), " is my name")
        self.assertTStringEqual(t, ("", " is my name"), [("Maria", "name")])
        self.assertEqual(fstring(t), "Maria is my name")

        # Should append empty string
        t = Template("Hello, ", Interpolation("Maria", "name", None, ""))
        self.assertTStringEqual(t, ("Hello, ", ""), [("Maria", "name")])
        self.assertEqual(fstring(t), "Hello, Maria")

        # Should concatenate strings
        t = Template("Hello", ", ", Interpolation("Maria", "name", None, ""), "!")
        self.assertTStringEqual(t, ("Hello, ", "!"), [("Maria", "name")])
        self.assertEqual(fstring(t), "Hello, Maria!")

        # Should add strings on either side and in between
        t = Template(
            Interpolation("Maria", "name", None, ""),
            Interpolation("Python", "language", None, ""),
        )
        self.assertTStringEqual(
            t, ("", "", ""), [("Maria", "name"), ("Python", "language")]
        )
        self.assertEqual(fstring(t), "MariaPython")

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_template_values(self):
        t = generate_template("Hello, world")
        self.assertEqual(t.values, ())

        name = "Lys"
        t = generate_template("Hello, {name}")
        self.assertEqual(t.values, ("Lys",))

        country = "GR"
        age = 0
        t = generate_template("Hello, {name}, {age} from {country}")
        self.assertEqual(t.values, ("Lys", 0, "GR"))

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_template_values_without_locals(self):
        t = generate_template("Hello, world")
        self.assertEqual(t.values, ())

        name = "Lys"
        t = generate_template("Hello, {name}")
        self.assertEqual(t.values, ("Lys",))

        country = "GR"
        age = 0
        t = generate_template("Hello, {name}, {age} from {country}")
        self.assertEqual(t.values, ("Lys", 0, "GR"))

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_pickle_template(self):
        user = "test"
        for template in (
            generate_template(""),
            generate_template("No values"),
            generate_template("With inter {user}"),
            generate_template("With ! {user!r}"),
            generate_template("With format {1 / 0.3:.2f}"),
            Template(),
            Template("a"),
            Template(Interpolation("Nikita", "name", None, "")),
            Template("a", Interpolation("Nikita", "name", "r", "")),
        ):
            for proto in range(pickle.HIGHEST_PROTOCOL + 1):
                with self.subTest(proto=proto, template=template):
                    pickled = pickle.dumps(template, protocol=proto)
                    unpickled = pickle.loads(pickled)

                    self.assertEqual(unpickled.values, template.values)
                    self.assertEqual(fstring(unpickled), fstring(template))

    @patch("tstr._interpolation_tools.Interpolation", compat.Interpolation)
    @patch("tstr._template_tools.Template", compat.Template)
    @patch("tstr._template_tools.Interpolation", compat.Interpolation)
    def test_pickle_interpolation(self):
        for interpolation in (
            Interpolation("Nikita", "name", None, ""),
            Interpolation("Nikita", "name", "r", ""),
            Interpolation(1 / 3, "x", None, ".2f"),
        ):
            for proto in range(pickle.HIGHEST_PROTOCOL + 1):
                with self.subTest(proto=proto, interpolation=interpolation):
                    pickled = pickle.dumps(interpolation, protocol=proto)
                    unpickled = pickle.loads(pickled)

                    self.assertEqual(unpickled.value, interpolation.value)
                    self.assertEqual(unpickled.expression, interpolation.expression)
                    self.assertEqual(unpickled.conversion, interpolation.conversion)
                    self.assertEqual(unpickled.format_spec, interpolation.format_spec)


class TemplateIterTests(unittest.TestCase):
    def test_abc(self):
        self.assertIsInstance(iter(t('')), Iterable)
        self.assertIsInstance(iter(t('')), Iterator)

    def test_final(self):
        TemplateIter = type(iter(t('')))
        with self.assertRaisesRegex(TypeError, 'is not an acceptable base type'):
            class Sub(TemplateIter): ...

    def test_iter(self):
        x = 1
        res = list(iter(t('abc {x} yz')))

        self.assertEqual(res[0], 'abc ')
        self.assertIsInstance(res[1], Interpolation)
        self.assertEqual(res[1].value, 1)
        self.assertEqual(res[1].expression, 'x')
        self.assertEqual(res[1].conversion, None)
        self.assertEqual(res[1].format_spec, '')
        self.assertEqual(res[2], ' yz')

    def test_exhausted(self):
        # See https://github.com/python/cpython/issues/134119.
        template_iter = iter(t("{1}"))
        self.assertIsInstance(next(template_iter), Interpolation)
        self.assertRaises(StopIteration, next, template_iter)
        self.assertRaises(StopIteration, next, template_iter)


class TestFunctions(unittest.TestCase):
    def test_convert(self):
        from fractions import Fraction

        for obj in ('Café', None, 3.14, Fraction(1, 2)):
            with self.subTest(f'{obj=}'):
                self.assertEqual(convert(obj, None), obj)
                self.assertEqual(convert(obj, 's'), str(obj))
                self.assertEqual(convert(obj, 'r'), repr(obj))
                self.assertEqual(convert(obj, 'a'), ascii(obj))

                # Invalid conversion specifier
                with self.assertRaises(ValueError):
                    convert(obj, 'z')
                with self.assertRaises(ValueError):
                    convert(obj, 1)
                with self.assertRaises(ValueError):
                    convert(obj, object())
