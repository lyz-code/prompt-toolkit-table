"""Define the models of the program."""

from functools import lru_cache
from typing import Any, List, Optional, Tuple

from prompt_toolkit.layout.dimension import Dimension
from pydantic import BaseModel  # noqa: E0611

StyleAndTextTuples = List[Tuple[str, str]]
Line = List[str]
CellLines = List[str]


class _Row:
    """Gather common methods of the header and the rows."""

    def __init__(
        self,
        cells: List[str],
        columns: List[str],
        padding: int = 1,
        separator: str = " ",
        style: str = "",
    ) -> None:
        """Initialize a generic table row.

        Args:
            columns: the columns to print.
            padding: number of spaces to add at the start and end of each column
            separator: character to separate each column
        """
        self.cells = cells
        self.columns = columns
        self.padding = padding
        self.separator = separator
        self._style = style
        self.widths = self._create_widths()

    @property
    def style(self) -> str:
        """Return the style of the row."""
        return self._style

    def _create_widths(self) -> List[Dimension]:
        """Calculate the preferred dimensions of a row.

        Also set the dimensions of the pads to not grow by setting it's width to 0.
        """
        dimensions: List[Dimension] = []
        for cell in self.cells:
            # We need to add 2 * self.padding characters for each cell because the
            # padding is added before and after the cell text.
            max_sentence_size = max([len(sentence) for sentence in cell.splitlines()])
            dimensions.append(
                Dimension(min=3, preferred=max_sentence_size + 2 * self.padding)
            )

            # Add the separator
            separator_size = len(self.separator)
            dimensions.append(
                Dimension(
                    min=separator_size,
                    max=separator_size,
                    preferred=separator_size,
                    weight=0,
                )
            )
        # Remove the last separator, and add the right margin
        dimensions.pop(-1)
        dimensions.append(Dimension(min=1, preferred=1, weight=0))
        return dimensions

    def create_text(self, row_widths: Tuple[int, ...]) -> StyleAndTextTuples:
        """Create the styles and text tuple for the row with the desired widths."""
        text_lines = self._wrap_row(row_widths)
        return self._create_style_and_text_tuples(text_lines)

    @lru_cache()
    def _wrap_row(self, column_widths: Tuple[int, ...]) -> List[Line]:
        """Wrap the row cells to match the width."""
        # Prepare the row elements: wrap the cells text, add the separator and
        # add the right margin.
        row_elements: List[CellLines] = []

        for cell_index in range(len(self.cells)):
            # Split the cell text into the required lines to fit the width
            # We need a step of 2 in the loop to skip the dimension of the separator
            width = column_widths[cell_index * 2]
            text = self.cells[cell_index]
            text_index = 0
            cell_lines = []
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
                            cell_lines.append(" ".ljust(width))
                            text_index += 1
                        text_index += 1
                        continue
                    else:
                        selected_text = selected_text[:break_index]
                        new_index = text_index + break_index
                cell_lines.append(f" {selected_text.strip()} ".ljust(width))
                text_index = new_index
            row_elements.append(cell_lines)

            # Add the separator
            row_elements.append([self.separator])
        # Remove the last separator, and add the right margin
        row_elements.pop(-1)
        row_elements.append([" " * column_widths[-1]])

        # Make sure that all row elements have the same number of lines
        max_height = max(len(element_lines) for element_lines in row_elements)
        for element_index in range(len(row_elements)):
            element_lines = row_elements[element_index]
            element_width = column_widths[element_index]
            missing_lines = max_height - len(element_lines)
            if missing_lines != 0:
                element_lines += [" " * element_width for _ in range(missing_lines)]

        # Merge line contents
        lines: List[Line] = []
        for line_number in range(max_height):
            line: Line = []
            for element_lines in row_elements:
                line.append(element_lines[line_number])
            lines.append(line)

        return lines

    def _create_style_and_text_tuples(self, lines: List[Line]) -> StyleAndTextTuples:
        """Apply the row style to the row lines and join them."""
        style_and_text: StyleAndTextTuples = []
        style = self.style
        for line in lines:
            for text in line:
                style_and_text.append((style, text))
            style_and_text.append((style, "\n"))
        return style_and_text


class Header(_Row):
    """Model the header of the table."""

    def __init__(
        self,
        table_data: List[Any],
        columns: Optional[List[str]] = None,
        style: str = "class:header",
        padding: int = 1,
        separator: str = " ",
    ) -> None:
        """Initialize the header.

        Args:
            table_data: the table data to print.
            columns: the columns to print.
            style: a prompt toolkit compatible style for the header.
            padding: number of spaces to add at the start and end of each column
            separator: character to separate each column
        """
        if columns is not None:
            columns = columns
        else:
            columns = self._guess_columns(table_data)
        super().__init__(
            cells=columns,
            columns=columns,
            padding=padding,
            separator=separator,
            style=style,
        )

    def _guess_columns(self, table_data: List[Any]) -> List[str]:
        """Guess the columns of the header from the table data.

        Args:
            table_data: the table data to print.
            style: a prompt toolkit compatible style for the header.
        """
        if isinstance(table_data[0], list):  # If is a list of lists
            raise ValueError("You need to specify a header for the table.")
        elif isinstance(table_data[0], dict):  # If is a list of dictionaries
            return [key.title() for key in table_data[0].keys()]
        elif isinstance(table_data[0], BaseModel):  # If is a list of pydantic objects
            return [
                property_["title"]
                for _, property_ in table_data[0].schema()["properties"].items()
            ]
        raise ValueError(
            "Table data format not supported, please enter a list of list of strings,"
            " a list of dictionaries or a list of pydantic objects."
        )

    def create_text(self, row_widths: Tuple[int, ...]) -> StyleAndTextTuples:
        """Create the styles and text tuple for the row with the desired widths.

        It also adds the line separating the header of the table data.
        """
        header_text = super().create_text(row_widths)

        # Extend the style over the scrollbar (that we don't have in the header)
        # Otherwise you get a black pixel
        last = header_text[-2]
        header_text[-2] = (last[0], last[1] + " ")

        separator_text = []
        for part in header_text:
            separator_text.append((part[0], "─" * len(part[1])))
        # remove the last \n substitution
        separator_text.pop(-1)
        return header_text + separator_text


class Row(_Row):
    """Model a row of the table."""

    def __init__(
        self,
        id_: int,
        row_data: List[Any],
        columns: List[str],
        style: str = "class: row",
        focused: bool = False,
        padding: int = 1,
        separator: str = " ",
    ) -> None:
        """Initialize the row.

        Args:
            row_data: the row data to process.
            columns: the columns to print.
            style: a prompt toolkit compatible style for the row.
            focused: if the row has the focus
            padding: number of spaces to add at the start and end of each column
            separator: character to separate each column
        """
        self.id_ = id_
        self.data = row_data
        self.focused = False
        cells = self._create_cells(row_data, columns)
        super().__init__(
            cells=cells,
            columns=columns,
            padding=padding,
            separator=separator,
            style=style,
        )

    @property
    def style(self) -> str:
        """Return the style of the row."""
        if self.focused:
            return f"{self._style},focused,[SetCursorPosition]"
        return self._style

    def focus(self) -> None:
        """Set the focus in the row."""
        self.focused = True

    def unfocus(self) -> None:
        """Unset the focus in the row."""
        self.focused = False

    @staticmethod
    def _create_cells(row_data: List[Any], columns: List[str]) -> List[str]:
        """Extract the cell content from the data."""
        if isinstance(row_data, list):
            if len(row_data) != len(columns):
                raise ValueError(
                    f"Row {row_data} length is different from the columns {columns}"
                )
            return [str(element) for element in row_data]
        if isinstance(row_data, BaseModel):
            return [
                str(getattr(row_data, key))
                for key, value in row_data.schema()["properties"].items()
                if value["title"] in columns
            ]
        if isinstance(row_data, dict):
            return [
                row_data[key]
                for key, value in row_data.items()
                if key.title() in columns
            ]

    def __hash__(self) -> int:
        """Create an unique hash of the class object."""
        return hash(self.id_)
