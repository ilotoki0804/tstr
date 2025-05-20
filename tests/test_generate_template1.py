# type: ignore
# Source: cpython/Lib/test/test_string/test_tstr.py

from __future__ import annotations

import pickle
from unittest.mock import patch

from _support import TStringTestCase, fstring, lib

import tstr._compat as compat
from tstr import Interpolation, Template, generate_template


class TestTemplate(TStringTestCase):
    @patch("tstr._utils.Template", compat.Template)
    @patch("tstr._utils.Interpolation", compat.Interpolation)
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

    @patch("tstr._utils.Template", compat.Template)
    @patch("tstr._utils.Interpolation", compat.Interpolation)
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

    @patch("tstr._utils.Template", compat.Template)
    @patch("tstr._utils.Interpolation", compat.Interpolation)
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

    @patch("tstr._utils.Template", compat.Template)
    @patch("tstr._utils.Interpolation", compat.Interpolation)
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

    @patch("tstr._utils.Template", compat.Template)
    @patch("tstr._utils.Interpolation", compat.Interpolation)
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

    @patch("tstr._utils.Template", compat.Template)
    @patch("tstr._utils.Interpolation", compat.Interpolation)
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

    @patch("tstr._utils.Template", compat.Template)
    @patch("tstr._utils.Interpolation", compat.Interpolation)
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
