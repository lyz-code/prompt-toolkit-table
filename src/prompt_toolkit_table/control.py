"""Define the TableControl."""

from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple

from prompt_toolkit.filters import FilterOrBool
from prompt_toolkit.layout import FormattedTextControl
from prompt_toolkit.layout.dimension import (
    Dimension,
    max_layout_dimensions,
    sum_layout_dimensions,
)
from prompt_toolkit.utils import take_using_weights
from pydantic import BaseModel  # noqa: E0611

if TYPE_CHECKING:
    from prompt_toolkit.data_structures import Point
    from prompt_toolkit.key_binding.key_bindings import KeyBindingsBase
    from prompt_toolkit.layout import UIContent

TableData = List[Any]
GetCursorPosition = Callable[[], Optional["Point"]]
CellSize = Tuple[int, int]
RowSize = List[CellSize]
StyleAndTextTuples = List[Tuple[str, str]]


class TableControl(FormattedTextControl):
    """Create table content with the correct format."""

    def __init__(
        self,
        data: TableData,
        header: Optional[List[str]] = None,
        padding: int = 1,
        padding_char: str = " ",
        padding_style: str = "padding",
        style: str = "",
        focusable: FilterOrBool = True,
        key_bindings: Optional["KeyBindingsBase"] = None,
        show_cursor: bool = True,
        modal: bool = False,
        get_cursor_position: Optional[GetCursorPosition] = None,
    ) -> None:
        """Prepare the control to manage the content."""
        if len(data) < 0:
            raise ValueError("Please introduce some data to print.")

        self.data = data
        self.header: List[str] = self._guess_header(header)
        self.padding = padding
        self.padding_char = padding_char
        self.padding_style = padding_style

        # Prepare the parent FormattedTextControl data.
        super().__init__(
            text=self.create_text,
            style=style,
            focusable=focusable,
            key_bindings=key_bindings,
            show_cursor=show_cursor,
            modal=modal,
            get_cursor_position=get_cursor_position,
        )

    def _guess_header(self, header: Optional[List[str]]) -> List[str]:
        """Guess the header from the input data."""
        if header is not None:
            return header

        if isinstance(self.data[0], list):  # If is a list of lists
            raise ValueError("You need to specify a header for the table.")
        elif isinstance(self.data[0], dict):  # If is a list of dictionaries
            return [key.title() for key in self.data[0].keys()]
        elif isinstance(self.data[0], BaseModel):  # If is a list of pydantic objects
            return [
                property_["title"]
                for _, property_ in self.data[0].schema()["properties"].items()
            ]
        raise ValueError(
            "Data format not supported, please enter a list of list of strings,"
            " a list of dictionaries or a list of pydantic objects."
        )

    def _get_row_dimensions(self, row: StyleAndTextTuples) -> List[Dimension]:
        """Calculate the preferred dimensions of a row.

        Also set the dimensions of the pads to not grow by setting it's width to 0.
        """
        dimensions: List[Dimension] = []
        for column in row:
            if "padding" in column[0]:
                dimension = Dimension(
                    min=self.padding, max=self.padding, preferred=self.padding, weight=0
                )
            elif "right_margin" in column[0]:
                dimension = Dimension(min=1, preferred=1, weight=0)
            else:
                # We need to add 2 characters for each column for the space before
                # and after the text
                max_sentence_size = max(
                    [len(sentence) for sentence in column[1].splitlines()]
                )
                dimension = Dimension(min=3, preferred=max_sentence_size + 2)

            dimensions.append(dimension)
        return dimensions

    def _create_rows(
        self, row_data: TableData, style: str = ""
    ) -> List[StyleAndTextTuples]:
        """Create rows with style and spaces between elements."""
        rows: List[StyleAndTextTuples] = []
        for row_data in row_data:
            # Set base style of the rows
            if style is not None:
                if len(rows) % 2 == 0:
                    style = "class:row.alternate"
                else:
                    style = "class:row"

            # Create the row elements with style and adding spaces around each element
            if isinstance(row_data, list):
                elements = [(style, str(element)) for element in row_data]
            elif isinstance(row_data, BaseModel):
                elements = [
                    (style, str(getattr(row_data, key)))
                    for key, value in row_data.schema()["properties"].items()
                    if value["title"] in self.header
                ]
            elif isinstance(row_data, dict):
                elements = [
                    (style, row_data[key])
                    for key, value in row_data.items()
                    if key.title() in self.header
                ]

            if len(elements) != len(self.header):
                raise ValueError(
                    "Row {row_data} length is different from the header {self.header}"
                )

            # Add the pads between elements
            row: StyleAndTextTuples = []
            if self.padding > 0:
                padding_style = f"{style},{self.padding_style}"
                for element in elements:
                    row.append(element)
                    row.append((padding_style, self.padding_char))
                row.pop(-1)

            # Add right margin.
            # We need it to be at least 1 character for the possible scrollbar
            row.append((f"{style},right_margin", " "))

            rows.append(row)
        return rows

    def _divide_widths(self, rows: List[StyleAndTextTuples], width: int) -> List[int]:
        """Return the widths for all columns based on their content.

        Inspired by VSplit._divide_widths.

        Raises:
            ValueError: if there is not enough space
        """
        row_widths = [self._get_row_dimensions(row) for row in rows]

        # Transpose it so we have a list of column dimensions, so we can get the max
        # dimensions per column.
        column_widths = [max_layout_dimensions(list(i)) for i in zip(*row_widths)]
        # Calculate widths.
        preferred_dimensions = [d.preferred for d in column_widths]

        # Sum dimensions
        sum_dimensions = sum_layout_dimensions(column_widths)

        # If there is not enough space for both.
        # Don't do anything.
        if sum_dimensions.min > width:
            raise ValueError("There is not enough space to print all the columns")

        # Find optimal sizes. (Start with minimal size, increase until we cover
        # the whole width.)
        sizes = [d.min for d in column_widths]

        child_generator = take_using_weights(
            items=list(range(len(column_widths))),
            weights=[d.weight for d in column_widths],
        )

        index = next(child_generator)

        # Increase until we meet at least the 'preferred' size.
        preferred_stop = min(width, sum_dimensions.preferred)

        while sum(sizes) < preferred_stop:
            if sizes[index] < preferred_dimensions[index]:
                sizes[index] += 1
            index = next(child_generator)

        # Set the right margin to use all the available space.
        sizes[-1] = max(sizes[-1], width - sum(sizes[:-1]))

        return sizes

    def _wrap_row(
        self, row: StyleAndTextTuples, column_widths: List[int]
    ) -> StyleAndTextTuples:
        """Wrap the contents of a row to match the width.

        Taking into account that as we have one space before and another after the
        content, each row that we add, adds two extra spaces to the content.
        """
        columns: List[StyleAndTextTuples] = []
        # Wrap the text of each column
        for column_index in range(len(row)):
            style = row[column_index][0]
            if "padding" in style:
                columns.append([row[column_index]])
                continue
            elif "right_margin" in style:
                columns.append([(style, " " * column_widths[column_index])])
                continue
            width = column_widths[column_index]
            text = row[column_index][1]
            text_index = 0
            column_lines = []
            min_width = max(text_index + width - 2, 1)
            while text_index <= len(text) - 1:
                new_index = text_index + min_width
                selected_text = text[text_index:new_index]
                # Deal with the new lines inside the cells
                if "\n" in selected_text:
                    break_index = selected_text.index("\n")
                    if break_index == 0:
                        # Deal with double \n\n
                        if selected_text[1] == "\n":
                            column_lines.append((style, " ".ljust(width)))
                            text_index += 1
                        text_index += 1
                        continue
                    else:
                        selected_text = selected_text[:break_index]
                        new_index = text_index + break_index
                column_lines.append((style, f" {selected_text.strip()} ".ljust(width)))
                text_index = new_index
            columns.append(column_lines)

        # Make sure that all columns have the same number of lines
        max_height = max(len(column_lines) for column_lines in columns)
        for column_index in range(len(columns)):
            column_lines = columns[column_index]
            width = column_widths[column_index]
            missing_lines = max_height - len(column_lines)
            if missing_lines != 0:
                column_lines += [
                    (column_lines[0][0], " " * width) for _ in range(missing_lines)
                ]

        # Merge row contents
        new_row = []
        for line in range(max_height):
            for column_lines in columns:
                new_row.append(column_lines[line])
            new_row.append(("", "\n"))

        return new_row

    def _pad_text(
        self, rows: List[StyleAndTextTuples], row_widths: List[int]
    ) -> StyleAndTextTuples:
        """Pad the text to adjust the desired size.

        Returns:
            header: padded header
            rows: padded rows.
        """
        padded_text: StyleAndTextTuples = []
        for row_index in range(len(rows)):
            padded_text += self._wrap_row(rows[row_index], row_widths)
        return padded_text

    def create_text(self, max_available_width: int = 300) -> StyleAndTextTuples:
        """Create the formatted text from the contents of the input data.

        Args:
            max_available_width: width to calculate the space for each column.

        Returns:
            Text split in rows with the fixed width of `max_available_width`, where
            each row is formed by a list of (style, text) tuples.
        """
        header = self._create_rows([self.header])[0]
        rows = self._create_rows(self.data)
        all_rows = [header] + rows

        # Adjust column widths to fit the max_available_width
        row_widths = self._divide_widths(all_rows, max_available_width)

        # Create the text
        self.header_text = self._pad_text([header], row_widths)
        return self._pad_text(rows, row_widths)

    def create_content(self, width: int, height: Optional[int]) -> "UIContent":
        """Transform the data into the UIContent object."""
        # Get fragments
        # ignore: Argument 1 to "append" of "list" has
        # incompatible type "List[Tuple[str, str]]";
        # expected "List[Union[Tuple[str, str],
        # Tuple[str, str, Callable[[MouseEvent], None]]]]"
        # But that type is in the allowed ones :S
        self.text = self.create_text(width)  # type: ignore
        return super().create_content(width, height)
