"""Test the implementation of the TableControl component."""

import re
from typing import TYPE_CHECKING, List

import pytest

from prompt_toolkit_table import TableControl

from ..conftest import DictData, ListData, PydanticData

if TYPE_CHECKING:
    from prompt_toolkit_table.control import StyleAndTextTuples


def get_lines(text: "StyleAndTextTuples") -> List["StyleAndTextTuples"]:
    """Transform the result text into a list of rows."""
    rows: List["StyleAndTextTuples"] = []
    row: "StyleAndTextTuples" = []
    for part in text:
        if re.match(r"\n$", part[1]):
            rows.append(row)
            row = []
        else:
            row.append(part)
    return rows


def get_columns(rows: List["StyleAndTextTuples"]) -> List["StyleAndTextTuples"]:
    """Transform the list of rows into a list of columns."""
    columns: List["StyleAndTextTuples"] = []
    for row in rows:
        for column_index in range(len(row)):
            try:
                columns[column_index].append(row[column_index])
            except IndexError:
                columns.append([row[column_index]])
    return columns


class TestTableControl:
    """Test the table control implementation."""

    def test_table_guess_header_of_list_of_pydantic_objects(
        self, pydantic_data: PydanticData
    ) -> None:
        """
        Given: A list of pydantic objects
        When: The TableControl is initialized with the list of objects
        Then: The header is well guessed
        """
        result = TableControl(pydantic_data)

        assert result.header == ["ID", "Name", "Bio"]

    def test_table_accepts_list_of_strings_with_header(
        self, list_data: ListData
    ) -> None:
        """
        Given: A list of strings
        When: The TableControl is initialized with the list of strings and the header
        Then: The header is well set
        """
        data, header = list_data

        result = TableControl(data, header=header)

        assert result.header == header

    def test_table_fails_if_list_of_strings_and_no_header(
        self, list_data: ListData
    ) -> None:
        """
        Given: A list of strings
        When: The TableControl is initialized with the list of strings
        Then: As there is no way of guessing the headers, return a ValueError exception
        """
        data, header = list_data

        with pytest.raises(
            ValueError, match="You need to specify a header for the table"
        ):
            TableControl(data)

    def test_table_guess_header_of_list_of_dictionaries(
        self, dict_data: DictData
    ) -> None:
        """
        Given: A list of dictionaries
        When: The TableControl is initialized with the list of dictionaries
        Then: The header is well guessed
        """
        result = TableControl(dict_data)

        assert result.header == [key.title() for key in dict_data[0].keys()]

    def test_table_creates_text_with_list_of_dicts(self, dict_data: DictData) -> None:
        """
        Given: A list of dictionaries
        When: The TableControl is initialized with the list of dictionaries
        Then: The text is well created, that means:
            * All cells of a row share the same style
            * The rows separate the cells with paddings
            * The rows have alternate styles
            * All cells of a column share the same length
        """
        control = TableControl(dict_data)

        result = control.create_text()

        lines = get_lines(result)
        for line in lines:
            # All cells of a row share the same base style
            for cell in line:
                # There is padding between content cells
                if line.index(cell) == len(line) - 1:
                    assert cell[0] == f"{line[0][0]},right_margin"
                elif line.index(cell) % 2 != 0:
                    assert cell[0] == f"{line[0][0]},padding"
                else:
                    assert cell[0] == line[0][0]
            # The rows have alternate styles
            if lines.index(line) % 2 != 0:
                assert line[0][0] == "class:row"
            else:
                assert line[0][0] == "class:row.alternate"
        # All cells of a column share the same length
        columns = get_columns(lines)
        for column in columns:
            for cell in column:
                assert len(cell[1]) == len(column[0][1])

    def test_table_creates_text_with_list_of_lists(self, list_data: ListData) -> None:
        """
        Given: A list of lists
        When: The TableControl is initialized with the list of lists
        Then: The text is well created, that means:
            * All cells of a row share the same style
            * The rows separate the cells with paddings
            * The rows have alternate styles
            * All cells of a column share the same length
        """
        data, header = list_data
        control = TableControl(data=data, header=header)

        result = control.create_text()

        lines = get_lines(result)
        for line in lines:
            # All cells of a row share the same base style
            for cell in line:
                # There is padding between content cells
                if line.index(cell) == len(line) - 1:
                    assert cell[0] == f"{line[0][0]},right_margin"
                elif line.index(cell) % 2 != 0:
                    assert cell[0] == f"{line[0][0]},padding"
                else:
                    assert cell[0] == line[0][0]
            # The rows have alternate styles
            if lines.index(line) % 2 != 0:
                assert line[0][0] == "class:row"
            else:
                assert line[0][0] == "class:row.alternate"
        # All cells of a column share the same length
        columns = get_columns(lines)
        for column in columns:
            for cell in column:
                assert len(cell[1]) == len(column[0][1])

    def test_table_creates_text_with_list_pydantic(
        self, pydantic_data: PydanticData
    ) -> None:
        """
        Given: A list of lists
        When: The TableControl is initialized with the list of lists
        Then: The text is well created, that means:
            * All cells of a row share the same style
            * The rows separate the cells with paddings
            * The rows have alternate styles
            * All cells of a column share the same length
        """
        control = TableControl(pydantic_data)

        result = control.create_text()

        lines = get_lines(result)
        for line in lines:
            # All cells of a row share the same base style
            for cell in line:
                # There is padding between content cells
                if line.index(cell) == len(line) - 1:
                    assert cell[0] == f"{line[0][0]},right_margin"
                elif line.index(cell) % 2 != 0:
                    assert cell[0] == f"{line[0][0]},padding"
                else:
                    assert cell[0] == line[0][0]
            # The rows have alternate styles
            if lines.index(line) % 2 != 0:
                assert line[0][0] == "class:row"
            else:
                assert line[0][0] == "class:row.alternate"
        # All cells of a column share the same length
        columns = get_columns(lines)
        for column in columns:
            for cell in column:
                assert len(cell[1]) == len(column[0][1])
