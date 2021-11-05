"""Test the implementation of the TableControl component."""

import re
from typing import TYPE_CHECKING, Any, List, Tuple

import pytest
from faker import Faker
from prompt_toolkit.application import Application, get_app
from prompt_toolkit.application.current import set_app
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyProcessor
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout, Window
from prompt_toolkit.layout.controls import UIContent
from prompt_toolkit.output import DummyOutput

from prompt_toolkit_table import TableControl

from ..conftest import DictData, ListData, PydanticData

if TYPE_CHECKING:
    from prompt_toolkit_table.model import StyleAndTextTuples


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

        assert result.header.columns == ["ID", "Name", "Bio"]

    def test_table_accepts_list_of_strings_with_header(
        self, list_data: ListData
    ) -> None:
        """
        Given: A list of strings
        When: The TableControl is initialized with the list of strings and the header
        Then: The header is well set
        """
        data, header = list_data

        result = TableControl(data, columns=header)

        assert result.header.columns == header

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

        assert result.header.columns == [key.title() for key in dict_data[0].keys()]

    def test_table_creates_text_with_list_of_dicts(self, dict_data: DictData) -> None:
        """
        Given: A list of dictionaries
        When: The TableControl is initialized with the list of dictionaries
        Then: The text is well created, that means:
            * All cells of a row share the same style
            * The rows separate the cells with paddings
            * The rows have alternate styles
            * All cells of a column share the same length
            * The first line is highlighted, and the cursor focus is set
        """
        control = TableControl(dict_data)

        control.create_content()  # act

        lines = get_lines(control.text)  # type: ignore
        for line in lines:
            # All cells of a row share the same base style
            for cell in line:
                assert cell[0] == line[0][0]
            # The rows have alternate styles
            if lines.index(line) == 0:
                assert line[0][0] == "class:row.alternate,focused,[SetCursorPosition]"
            elif lines.index(line) % 2 != 0:
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
            * The first line is highlighted, and the cursor focus is set
        """
        data, header = list_data
        control = TableControl(table_data=data, columns=header)

        control.create_content()  # act

        lines = get_lines(control.text)  # type: ignore
        for line in lines:
            # All cells of a row share the same base style
            for cell in line:
                assert cell[0] == line[0][0]
            # The rows have alternate styles
            if lines.index(line) == 0:
                assert line[0][0] == "class:row.alternate,focused,[SetCursorPosition]"
            elif lines.index(line) % 2 != 0:
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
            * The first line is highlighted, and the cursor focus is set
        """
        control = TableControl(pydantic_data)

        control.create_content()  # act

        lines = get_lines(control.text)  # type: ignore
        for line in lines:
            # All cells of a row share the same base style
            for cell in line:
                assert cell[0] == line[0][0]
            # The rows have alternate styles
            if lines.index(line) == 0:
                assert line[0][0] == "class:row.alternate,focused,[SetCursorPosition]"
            elif lines.index(line) % 2 != 0:
                assert line[0][0] == "class:row"
            else:
                assert line[0][0] == "class:row.alternate"
        # All cells of a column share the same length
        columns = get_columns(lines)
        for column in columns:
            for cell in column:
                assert len(cell[1]) == len(column[0][1])

    def test_create_content_returns_the_expected_uicontent(
        self, pydantic_data: PydanticData
    ) -> None:
        """
        Given: A well configured table
        When: create_content is called
        Then: The UIContent object is well built and configured meaning:
            * the cursor is not shown
        """
        control = TableControl(pydantic_data)

        result = control.create_content(width=300)

        assert isinstance(result, UIContent)
        assert not result.show_cursor

    def test_raise_error_if_elements_len_different_header(
        self, list_data: ListData
    ) -> None:
        """
        Given: A wrong configured table, where the header is smaller than the elements
        When: create_content is initialized
        Then: a ValueError exception is raised
        """
        data, header = list_data
        data[0].pop(0)

        with pytest.raises(
            ValueError, match="Row.*length is different from the columns.*"
        ):
            TableControl(data, columns=header)

    def test_raise_error_if_no_data_is_entered(self) -> None:
        """
        Given: Nothing
        When: the component is initialized without data
        Then: a ValueError exception is raised
        """
        with pytest.raises(ValueError, match="Please introduce some data to print."):
            TableControl(table_data=[])

    def test_raise_error_if_wrong_data(self) -> None:
        """
        Given: A non supported data
        When: the component is initialized
        Then: a ValueError exception is raised
        """
        with pytest.raises(
            ValueError,
            match="Table data format not supported, please enter a list of .*",
        ):
            TableControl(table_data=[1])


class TestWrapping:
    """Test the wrapping of the table control."""

    def test_wrapping_long_column_in_the_middle(self, faker: Faker) -> None:
        """
        Given: A row with a long column in the middle
        When: create_content is called with a width that needs wrapping
        Then: The text is well wrapped, that means that all the cells of a column have
            the same size.
        """
        data = [["cell", faker.sentence(), "cell"]]
        header = ["head", "head", "head"]
        control = TableControl(table_data=data, columns=header)

        control.create_content(width=30)  # act

        lines = get_lines(control.text)  # type: ignore
        columns = get_columns(lines)
        for column in columns:
            for cell in column:
                assert len(cell[1]) == len(column[0][1])

    def test_wrapping_with_paragraph_that_matches_the_wrap(self) -> None:
        r"""
        Given: A row with a text with \n in a column in the middle, and the \n falls
            where the wrapping would split the lines
        When: create_content is called with a width that doesn't need wrapping
        Then: The text is well formatted, that means that:
            * The content should only have two lines.
            * The text should not contain the \n, instead, the wrapping should be done
                around that \n
        """
        data = [["cell", "hello\nworld", "cell"]]
        header = ["head", "head", "head"]
        control = TableControl(table_data=data, columns=header)

        control.create_content(width=40)  # act

        lines = get_lines(control.text)  # type: ignore
        assert len(lines) == 2
        assert lines[0][2][1] == " hello "
        assert lines[1][2][1] == " world "

    def test_wrapping_with_paragraph_that_doesnt_match_the_wrap(self) -> None:
        r"""
        Given: A row with a text with \n in a column in the middle, and the \n doesn't
            falls where the wrapping would split the lines.
        When: create_content is called with a width that doesn't need wrapping
        Then: The text is well formatted, that means that:
            * The content should only have two lines.
            * The text should not contain the \n, instead, the wrapping should be done
                around that \n
        """
        data = [["cell", "hello\nbeautiful world", "cell"]]
        header = ["head", "head", "head"]
        control = TableControl(table_data=data, columns=header)

        control.create_content(width=60)  # act

        lines = get_lines(control.text)  # type: ignore
        assert len(lines) == 2
        assert lines[0][2][1] == " hello           "
        assert lines[1][2][1] == " beautiful world "

    def test_wrapping_with_two_short_paragraphs(self, faker: Faker) -> None:
        r"""
        Given: A row with a text with two \n in a column in the middle
        When: create_content is called with a width that doesn't need wrapping
        Then: There are no \n in the text of the cells.
        """
        data = [["cell", "\n".join(faker.paragraphs()), "cell"]]
        header = ["head", "head", "head"]
        control = TableControl(table_data=data, columns=header)

        control.create_content(width=60000)  # act

        lines = get_lines(control.text)  # type: ignore
        assert "\n" not in lines[0][2][1]
        assert "\n" not in lines[1][2][1]
        assert "\n" not in lines[2][2][1]

    def test_wrapping_with_two_newlines(self) -> None:
        r"""
        Given: A row with a text with two consecutive \n in a column in the middle
        When: create_content is called with a width that doesn't need wrapping
        Then: There are no \n in the text of the cells, but an empty line is created
        """
        data = [["cell", "hello\n\nbeautiful world", "cell"]]
        header = ["head", "head", "head"]
        control = TableControl(table_data=data, columns=header)

        control.create_content(width=60000)  # act

        lines = get_lines(control.text)  # type: ignore
        assert len(lines) == 3
        assert lines[0][2][1] == " hello           "
        assert lines[1][2][1] == "                 "
        assert lines[2][2][1] == " beautiful world "

    def test_wrapping_returns_error_if_there_is_not_enough_space(self) -> None:
        r"""
        Given: A data with a minimum size that is greater than the available width
        When: create_content is called
        Then: A ValueError is returned
        """
        data = [["cell", "hello\n\nbeautiful world", "cell"]]
        header = ["head", "head", "head"]
        control = TableControl(table_data=data, columns=header)

        with pytest.raises(
            ValueError, match="There is not enough space to print all the columns"
        ):
            control.create_content(width=10)


def set_dummy_app(data: PydanticData) -> Any:
    """Return a context manager that starts the dummy application.

    This is important, because we need an `Application` with `is_done=False`
    flag, otherwise no keys will be processed.
    """
    app: Application[Any] = Application(
        layout=Layout(Window(TableControl(data))),
        output=DummyOutput(),
        input=create_pipe_input(),
    )

    return set_app(app)


def get_content_and_processor() -> Tuple[TableControl, KeyProcessor]:
    """Return the content to test and the key processor."""
    app = get_app()
    key_bindings = app.layout.container.get_key_bindings()

    if key_bindings is None:
        key_bindings = KeyBindings()
    processor = KeyProcessor(key_bindings)

    # ignore: "Container" has no attribute "content" -> but it does have it.
    content = app.layout.container.content  # type: ignore
    return content, processor


class TestMovement:
    """Test the movement inside the TableControl."""

    @pytest.mark.parametrize("key", ["j", Keys.Down])
    def test_moves_to_the_next_row(self, pydantic_data: PydanticData, key: str) -> None:
        """
        Given: A well configured table
        When: j or down is press
        Then: the focus is moved to the next line
        """
        with set_dummy_app(pydantic_data):
            content, processor = get_content_and_processor()

            processor.feed(KeyPress(key, key))  # act

            processor.process_keys()
            assert content._focused_row == 1

    @pytest.mark.parametrize("key", ["k", Keys.Up])
    def test_moves_to_the_previous_row(
        self, pydantic_data: PydanticData, key: str
    ) -> None:
        """
        Given: A well configured table, and the highlight in the second row
        When: k or up is press
        Then: the focus is moved to the first line
        """
        with set_dummy_app(pydantic_data):
            content, processor = get_content_and_processor()
            content._focused_row = 1

            processor.feed(KeyPress(key, key))  # act

            processor.process_keys()
            assert content._focused_row == 0

    @pytest.mark.parametrize("key", [Keys.ControlD, Keys.PageDown])
    def test_moves_a_bunch_of_rows_down(
        self, pydantic_data: PydanticData, key: str
    ) -> None:
        """
        Given: A well configured table
        When: c-d or page down is press
        Then: the focus is moved a bunch of lines down
        """
        with set_dummy_app(pydantic_data):
            content, processor = get_content_and_processor()

            processor.feed(KeyPress(key, key))  # act

            processor.process_keys()
            assert content._focused_row == 9

    @pytest.mark.parametrize("key", [Keys.ControlU, Keys.PageUp])
    def test_moves_a_bunch_of_rows_up(
        self, pydantic_data: PydanticData, key: str
    ) -> None:
        """
        Given: A well configured table
        When: c-u or page up is press
        Then: the focus is moved a bunch of lines up
        """
        with set_dummy_app(pydantic_data):
            content, processor = get_content_and_processor()
            # Add rows so we have 12
            content.rows.append(content.rows[2])
            content.rows.append(content.rows[2])
            content._focused_row = 11

            processor.feed(KeyPress(key, key))  # act

            processor.process_keys()
            assert content._focused_row == 1

    @pytest.mark.parametrize("key", ["k", Keys.Up, Keys.ControlU, Keys.PageUp])
    def test_moves_up_never_goes_over_the_first_item(
        self, pydantic_data: PydanticData, key: str
    ) -> None:
        """
        Given: A well configured table and the focus in the first row
        When: any key that moves the focus up
        Then: the focus stays in the first row
        """
        with set_dummy_app(pydantic_data):
            content, processor = get_content_and_processor()

            processor.feed(KeyPress(key, key))  # act

            processor.process_keys()
            assert content._focused_row == 0

    @pytest.mark.parametrize("key", ["j", Keys.Down, Keys.ControlD, Keys.PageDown])
    def test_moves_down_never_goes_below_the_last_item(
        self, pydantic_data: PydanticData, key: str
    ) -> None:
        """
        Given: A well configured table and the focus in the last row
        When: any key that moves the focus down
        Then: the focus stays in the last row
        """
        with set_dummy_app(pydantic_data):
            content, processor = get_content_and_processor()
            last_row = len(content.data) - 1
            content._focused_row = last_row

            processor.feed(KeyPress(key, key))  # act

            processor.process_keys()
            assert content._focused_row == last_row

    def test_moves_to_the_top(self, pydantic_data: PydanticData) -> None:
        """
        Given: A well configured table and the focus in the last row
        When: gg is pressed
        Then: the focus goes to the first row
        """
        with set_dummy_app(pydantic_data):
            content, processor = get_content_and_processor()
            last_row = len(content.data) - 1
            content._focused_row = last_row
            processor.feed(KeyPress("g", "g"))

            processor.feed(KeyPress("g", "g"))  # act

            processor.process_keys()
            assert content._focused_row == 0

    def test_moves_to_the_bottom(self, pydantic_data: PydanticData) -> None:
        """
        Given: A well configured table and the focus in the first row
        When: G is pressed
        Then: the focus goes to the last row
        """
        with set_dummy_app(pydantic_data):
            content, processor = get_content_and_processor()
            last_row = len(content.data) - 1

            processor.feed(KeyPress("G"))  # act

            processor.process_keys()
            assert content._focused_row == last_row

    def test_find_finds_rows_below_the_current_row(
        self, pydantic_data: PydanticData
    ) -> None:
        """
        Given: A well configured table and the focus in the second row, and the
            first letter of the first column of the fourth row is x
        When: f and then x is pressed
        Then: the focus goes to the fourth row
        """
        with set_dummy_app(pydantic_data):
            content, processor = get_content_and_processor()
            content._focused_row = 1
            content.rows[3].cells[0] = "xwebhe"
            content.create_content()
            processor.feed(KeyPress("f"))

            processor.feed(KeyPress("x"))  # act

            processor.process_keys()
            assert content._focused_row == 3

    def test_find_finds_rows_above_the_current_row(
        self, pydantic_data: PydanticData
    ) -> None:
        """
        Given: A well configured table and the focus in the second row, and the
            first letter of the first column of the first row is x, and none of
            the rows below the first one start with x
        When: f and then x is pressed
        Then: the focus goes to the first row
        """
        with set_dummy_app(pydantic_data):
            content, processor = get_content_and_processor()
            content._focused_row = 1
            content.rows[0].cells[0] = "xwebhe"
            content.create_content()
            processor.feed(KeyPress("f"))

            processor.feed(KeyPress("x"))  # act

            processor.process_keys()
            assert content._focused_row == 0

    def test_backward_find_finds_rows_above_the_current_row(
        self, pydantic_data: PydanticData
    ) -> None:
        """
        Given: A well configured table and the focus in the fourth row, and the
            first letter of the first column of the second and fifth rows is x
        When: F and then x is pressed
        Then: the focus goes to the second row
        """
        with set_dummy_app(pydantic_data):
            content, processor = get_content_and_processor()
            content._focused_row = 3
            content.rows[1].cells[0] = "xwebhe"
            content.rows[4].cells[0] = "xebhwe"
            content.create_content()
            processor.feed(KeyPress("F"))

            processor.feed(KeyPress("x"))  # act

            processor.process_keys()
            assert content._focused_row == 1

    def test_backward_find_finds_rows_below_the_current_row(
        self, pydantic_data: PydanticData
    ) -> None:
        """
        Given: A well configured table and the focus in the second row, and the
            first letter of the first column of the fourth row is x, and none of
            the rows above the second one start with x
        When: F and then x is pressed
        Then: the focus goes to the fourth row
        """
        with set_dummy_app(pydantic_data):
            content, processor = get_content_and_processor()
            content._focused_row = 1
            content.rows[3].cells[0] = "xwebhe"
            content.create_content()
            processor.feed(KeyPress("F"))

            processor.feed(KeyPress("x"))  # act

            processor.process_keys()
            assert content._focused_row == 3
