"""Define the TableControl."""

from functools import lru_cache
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple

from prompt_toolkit.filters import FilterOrBool
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase, merge_key_bindings
from prompt_toolkit.key_binding.key_bindings import _MergedKeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import FormattedTextControl
from prompt_toolkit.layout.dimension import max_layout_dimensions, sum_layout_dimensions
from prompt_toolkit.utils import take_using_weights

from prompt_toolkit_table.model import Header

from .model import Row

if TYPE_CHECKING:
    from prompt_toolkit.data_structures import Point
    from prompt_toolkit.layout import UIContent

TableData = List[Any]
GetCursorPosition = Callable[[], Optional["Point"]]
CellSize = Tuple[int, int]
RowSize = List[CellSize]


class TableControl(FormattedTextControl):
    """Create table content with the correct format."""

    def __init__(
        self,
        table_data: TableData,
        columns: Optional[List[str]] = None,
        padding: int = 1,
        separator: str = " ",
        style: str = "",
        focusable: FilterOrBool = True,
        key_bindings: Optional[KeyBindingsBase] = None,
        show_cursor: bool = True,
        modal: bool = False,
        get_cursor_position: Optional[GetCursorPosition] = None,
    ) -> None:
        """Prepare the control to manage the content."""
        if len(table_data) == 0:
            raise ValueError("Please introduce some data to print.")

        self.data = table_data
        self.header = Header(
            table_data=table_data, columns=columns, padding=padding, separator=separator
        )
        self.rows = self._create_rows(
            table_data, self.header.columns, padding, separator
        )
        self._focused_row = 0

        # Key bindings.
        control_bindings = self.create_bindings(key_bindings)

        # Prepare the parent FormattedTextControl data.
        super().__init__(
            text=self.create_content,
            style=style,
            focusable=focusable,
            key_bindings=control_bindings,
            show_cursor=False,
            modal=modal,
            get_cursor_position=get_cursor_position,
        )

    @staticmethod
    def _create_rows(
        rows_data: TableData, columns: List[str], padding: int, separator: str
    ) -> List[Row]:
        """Create rows with style and spaces between elements."""
        rows: List[Row] = []
        for row_index in range(len(rows_data)):
            # Set base style of the rows
            if row_index % 2 == 0:
                style = "class:row.alternate"
            else:
                style = "class:row"

            # Set the focus in the first row
            row = Row(
                id_=row_index,
                row_data=rows_data[row_index],
                columns=columns,
                style=style,
                padding=padding,
                separator=separator,
            )
            if row_index == 0:
                row.focus()
            rows.append(row)
        return rows

    def create_bindings(
        self, key_bindings: Optional[KeyBindingsBase]
    ) -> _MergedKeyBindings:
        """Configure the control bindings."""
        if key_bindings is None:
            key_bindings = KeyBindings()
        control_bindings = KeyBindings()

        @control_bindings.add("k")
        @control_bindings.add("up")
        def _up(event: KeyPressEvent) -> None:
            """Move the focus one row up."""
            self.focus_row(max(0, self._focused_row - 1))

        @control_bindings.add("down")
        @control_bindings.add("j")
        def _down(event: KeyPressEvent) -> None:
            """Move the focus one row down."""
            self.focus_row(min(len(self.data) - 1, self._focused_row + 1))

        @control_bindings.add("c-u")
        @control_bindings.add("pageup")
        def _pageup(event: KeyPressEvent) -> None:
            """Move the focus ten rows up."""
            self.focus_row(max(0, self._focused_row - 10))

        @control_bindings.add("c-d")
        @control_bindings.add("pagedown")
        def _pagedown(event: KeyPressEvent) -> None:
            """Move the focus ten rows down."""
            self.focus_row(min(len(self.data) - 1, self._focused_row + 10))

        @control_bindings.add("g", "g")
        def _top(event: KeyPressEvent) -> None:
            """Move the focus to the top."""
            self._focused_row = 0
            self.focus_row(0)

        @control_bindings.add("G")
        def _bottom(event: KeyPressEvent) -> None:
            """Move the focus to the bottom."""
            self.focus_row(len(self.data) - 1)

        @control_bindings.add("f", Keys.Any)
        def _find_rows(event: KeyPressEvent) -> None:
            """Find rows whose first column cell starts with the pressed key.

            We first check values after the selected value, then all values.
            """
            values = [row.cells[0] for row in self.rows]
            # E203: white space introduced by black
            for value in values[self._focused_row + 1 :] + values:  # noqa: E203
                if value.lower().startswith(event.data.lower()):
                    self._focused_row = values.index(value)
                    return

        @control_bindings.add("F", Keys.Any)
        def _backward_find_rows(event: KeyPressEvent) -> None:
            """Find backwards rows whose first column cell starts with the pressed key.

            We first check values before the selected value, then all values.
            """
            values = [row.cells[0] for row in self.rows]
            # E203: white space introduced by black
            for value in values[: self._focused_row - 1][::-1] + values:  # noqa: E203
                if value.lower().startswith(event.data.lower()):
                    self._focused_row = values.index(value)
                    return

        return merge_key_bindings([key_bindings, control_bindings])

    def create_content(
        self, width: int = 300, height: Optional[int] = None
    ) -> "UIContent":
        """Transform the data into the UIContent object.

        Args:
            width: terminal width
            height: terminal height
        """
        # Adjust column widths to fit the terminal width
        row_widths = self._divide_widths(width)

        # Create the text
        self.header_text = self.header.create_text(row_widths)

        self.text = []
        for row in self.rows:
            self.text += row.create_text(row_widths)
        return super().create_content(width, height)

    @lru_cache()
    def _divide_widths(self, width: int) -> Tuple[int, ...]:
        """Return the widths for all columns based on their content.

        Inspired by VSplit._divide_widths.

        We need the return value to be a tuple because we need to hash it later for the
        lru_cache.

        Raises:
            ValueError: if there is not enough space
        """
        row_widths = [row.widths for row in self.rows]
        row_widths.append(self.header.widths)

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

        return tuple(sizes)

    def focus_row(self, index: int) -> None:
        """Set the focus at the row in that index."""
        self.rows[self._focused_row].unfocus()
        self._focused_row = index
        self.rows[self._focused_row].focus()
