import io
import logging

import pytest

from tstr import generate_template, render
from tstr.ext._logging import TemplateFormatter, install, logging_context, uninstall


def test_template_logging():
    logger = logging.getLogger("tstr.test")
    logger.setLevel(logging.INFO)

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(TemplateFormatter())
    logger.addHandler(handler)

    name = "world"
    template = generate_template("Hello, {name}!")
    logger.info(template)
    handler.flush()
    output = stream.getvalue()
    assert "Hello, world!\n" == output

    logger.removeHandler(handler)


@pytest.mark.parametrize("renderer", [TemplateFormatter.execute_callable, TemplateFormatter().execute_callable])
def test_template_logging_with_execute_function_formatter(renderer):
    logger = logging.getLogger("tstr.test")
    logger.setLevel(logging.INFO)

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(TemplateFormatter(renderer=renderer))
    logger.addHandler(handler)

    def run():
        name = "world"
        compute = lambda: 2345 * 346 - 23  # noqa
        return generate_template("Hello, {name}, {compute}!")

    template = run()
    logger.info(template)
    handler.flush()
    output = stream.getvalue()
    assert "Hello, world, 811347!\n" == output

    logger.removeHandler(handler)


def test_template_formatter():
    formatter = TemplateFormatter()
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)

    logger = logging.getLogger("test_formatter")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    name = "World"
    template = generate_template("Hello {name}!")
    logger.info(template)

    assert "Hello World!" in stream.getvalue()


def test_install_uninstall():
    # Save original formatter
    logging.basicConfig()
    handler = logging.root.handlers[0]
    original_formatter = handler.formatter

    # Test install
    install()
    assert isinstance(handler.formatter, TemplateFormatter)

    # Test uninstall
    uninstall()
    assert handler.formatter is original_formatter


def test_logging_context():
    logging.basicConfig()
    handler = logging.root.handlers[0]
    original_formatter = handler.formatter

    stream = io.StringIO()
    test_handler = logging.StreamHandler(stream)
    test_logger = logging.getLogger("context_test")
    test_logger.addHandler(test_handler)
    test_logger.setLevel(logging.INFO)
    test_logger.propagate = False

    with logging_context():
        assert isinstance(handler.formatter, TemplateFormatter)
        x = 42
        template = generate_template("Value is {x}")
        logging.info(template)

    assert handler.formatter is original_formatter


def test_custom_renderer():
    def custom_render(template):
        return f"CUSTOM: {render(template)}"

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    formatter = TemplateFormatter(renderer=custom_render)
    handler.setFormatter(formatter)

    logger = logging.getLogger("custom_test")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    value = 123
    template = generate_template("Number: {value}")
    logger.info(template)

    assert "CUSTOM: Number: 123" in stream.getvalue()


def test_shadow_formatter():
    base_formatter = logging.Formatter("%(levelname)s: %(message)s")
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(base_formatter)

    logger = logging.getLogger("shadow_test")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    TemplateFormatter.shadow(handler, None)

    key = "Item"
    value = "Test"
    logger.info("Regular message")
    template = generate_template("{key}: {value}")
    logger.info(template)

    log_output = stream.getvalue()
    assert "INFO: Regular message" in log_output
    assert "INFO: Item: Test" in log_output
