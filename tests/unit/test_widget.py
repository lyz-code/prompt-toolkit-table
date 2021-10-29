"""Test the Table widget."""

from typing import Any

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import set_app
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.output import DummyOutput

from prompt_toolkit_table import Table

from ..conftest import PydanticData


def set_dummy_app(data: PydanticData) -> Any:
    """Return a context manager that starts the dummy application.

    This is important, because we need an `Application` with `is_done=False`
    flag, otherwise no keys will be processed.
    """
    app: Application[Any] = Application(
        layout=Layout(Table(data)),
        output=DummyOutput(),
        input=create_pipe_input(),
    )

    return set_app(app)


class TestTable:
    """Test the table implementation."""

    def test_table_contains_all_elements_by_default(
        self, pydantic_data: PydanticData
    ) -> None:
        """
        Given: A well configured table
        When: Initialized
        Then: it contains header, separator and body, where:
            * The header and separator have the header style, are not focusable
                and have no cursor position
            * The header and separator have no \n

        """
        result = Table(pydantic_data)

        assert isinstance(result.window, HSplit)
        # ignore: window has no attribute content, but it does
        header = result.window.children[0].content.text()  # type: ignore
        separator = result.window.children[1].content.text()  # type: ignore
        for part in header + separator:
            assert "class:header" in part[0]
            assert "focused" not in part[0]
            assert "[SetCursorPosition]" not in part[0]
            assert "\n" not in part[1]
