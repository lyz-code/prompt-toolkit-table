"""Test the implementation of the Table widget."""

import pytest
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import Layout

from prompt_toolkit_table import Table

from ..conftest import DictData, ListData, PydanticData


class TestBindings:
    """Test the bindings of the Table."""

    def test_table_default_bindings(self, dict_data: DictData) -> None:
        """
        Given: A Table object
        When: initialized without any binding
        Then: The default bindings are set.
        """
        result = Table(dict_data)

        assert result.key_bindings is not None
        bindings = result.key_bindings.bindings
        assert len(bindings) == 2
        for binding in bindings:
            if binding.keys == ("j",):
                assert binding.handler == focus_next
            elif binding.keys == ("k",):
                assert binding.handler == focus_previous

    def test_table_merges_bindings(self, dict_data: DictData) -> None:
        """
        Given: A Table object and some new bindings
        When: initialized with the new bindings
        Then: the default bindings are overwritten

        In prompt_toolkit the merge_key_bindings doesn't overwrite the existing
        bindings, instead it adds them to the end and I guess the `eager` will take
        preference.
        """
        new_bindings = KeyBindings()
        new_bindings.add("j", eager=True)(focus_previous)

        result = Table(dict_data, key_bindings=new_bindings)

        assert result.key_bindings is not None
        bindings = result.key_bindings.bindings
        assert len(bindings) == 3
        for binding in bindings:
            if binding.keys == ("j",) and not binding.eager():
                assert binding.handler == focus_next
            elif binding.keys == ("j",) and binding.eager():
                assert binding.handler == focus_previous
            elif binding.keys == ("k",):
                assert binding.handler == focus_previous


class TestTable:
    """Test the table implementation."""

    def test_table_accepts_list_of_pydantic_objects(
        self, pydantic_data: PydanticData
    ) -> None:
        """
        Given: A list of pydantic objects
        When: The Table is initialized with the list of objects
        Then: The rows are created correctly
        """
        result = Table(pydantic_data)

        assert len(result.rows) == 11
        assert result.header == ["ID", "Name", "Bio"]

    def test_table_accepts_list_of_strings(self, list_data: ListData) -> None:
        """
        Given: A list of strings
        When: The Table is initialized with the list of strings and the header
        Then: The rows are created correctly
        """
        data, header = list_data

        result = Table(data, header=header)

        assert len(result.rows) == len(data) + 1
        assert result.header == header

    def test_table_fails_if_list_of_strings_and_no_header(
        self, list_data: ListData
    ) -> None:
        """
        Given: A list of strings
        When: The Table is initialized with the list of strings
        Then: As there is no way of guessing the headers, return a ValueError exception
        """
        data, header = list_data

        with pytest.raises(
            ValueError, match="You need to specify a header for the table"
        ):
            Table(data)

    def test_table_accepts_list_of_dictionaries(self, dict_data: DictData) -> None:
        """
        Given: A list of dictionaries
        When: The Table is initialized with the list of dictionaries
        Then: The rows are created correctly
        """
        result = Table(dict_data)

        assert len(result.rows) == len(dict_data) + 1
        assert result.header == [key.title() for key in dict_data[0].keys()]

    def test_table_sets_the_rows_style(self, dict_data: DictData) -> None:
        """
        Given: A list of dictionaries
        When: The Table is initialized with the list of dictionaries
        Then: The rows are created with the styles set
        """
        result = Table(dict_data)

        assert result.rows[0].style == "class:row"
        assert result.rows[1].style == "class:row.alternate"
        assert result.rows[2].style == "class:row"
        for row in result.rows:
            assert row.columns[0].content.focusable()  # type: ignore

    def test_table_sets_the_header(self, dict_data: DictData) -> None:
        """
        Given: A list of dictionaries
        When: The Table is initialized with the list of dictionaries
        Then: The header is created with the style set and is not focusable
        """
        result = Table(dict_data)

        header = result.table_header
        assert header.style == "class:header"
        assert not header.children[0].content.focusable()  # type: ignore

    def test_table_sets_the_focus_row_style(self, dict_data: DictData) -> None:
        """
        Given: An initialized Table
        When: A row is focused
        Then: The style focused is set,
        """
        table = Table(dict_data)
        layout = Layout(table)

        layout.focus(table.children[0])  # act

        # ignore: str is not callable, but the style is indeed callable from the docs.
        __import__("pdb").set_trace()  # XXX BREAKPOINT
        assert table.rows[0].style() == "class:row.focused"  # type: ignore
