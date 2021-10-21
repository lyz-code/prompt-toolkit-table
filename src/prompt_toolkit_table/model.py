"""Define the Table python prompt toolkit widget."""

from typing import Callable, List, Optional, TypeVar, Union

from prompt_toolkit.application import get_app
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase, merge_key_bindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.containers import (
    Container,
    HorizontalAlign,
    HSplit,
    VerticalAlign,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import AnyDimension, max_layout_dimensions
from prompt_toolkit.layout.mouse_handlers import MouseHandlers
from prompt_toolkit.layout.screen import Screen, WritePosition
from prompt_toolkit.styles import Style
from pydantic import BaseModel  # noqa: E0611

# Table Key bindings

table_bindings = KeyBindings()

table_bindings.add("j")(focus_next)
table_bindings.add("k")(focus_previous)


# Styles

table_style = Style(
    [
        ("row", "bg:#002b36 #657b83"),
        ("row.alternate", "bg:#073642"),
        ("row.focused", "#268bd2"),
    ]
)

# Models

RowData = TypeVar("RowData")
TableData = List[RowData]


class Table(HSplit):
    """Define a table.

    Args:
        header
        data: Data to print
        handler: Called when the row is clicked, no parameters are passed to this
            callable.
    """

    def __init__(
        self,
        data: TableData[RowData],
        header: Optional[List[str]] = None,
        fill_width: bool = False,
        window_too_small: Optional[Container] = None,
        align: VerticalAlign = VerticalAlign.JUSTIFY,
        padding: AnyDimension = 0,
        padding_char: Optional[str] = None,
        padding_style: str = "",
        width: AnyDimension = None,
        height: AnyDimension = None,
        z_index: Optional[int] = None,
        modal: bool = False,
        key_bindings: Optional[KeyBindingsBase] = None,
        style: Union[str, Callable[[], str]] = "",
    ) -> None:
        """Initialize the widget."""
        self.fill_width = fill_width
        if header is None:
            if isinstance(data[0], list):  # If is a list of lists
                raise ValueError("You need to specify a header for the table")
            elif isinstance(data[0], dict):  # If is a list of dictionaries
                header = [key.title() for key in data[0].keys()]
            elif isinstance(data[0], BaseModel):  # If is a list of pydantic objects
                header = [
                    property["title"]
                    for _, property in data[0].schema()["properties"].items()
                ]

        self.data: List[RowData] = data
        self.header = header
        self.table_header = _Row(self.header, style="class:header", focusable=False)

        if key_bindings is None:
            key_bindings = KeyBindings()
        key_bindings = merge_key_bindings([table_bindings, key_bindings])

        self.rows = []
        for row in self.data:
            if style == "class:row":
                style = "class:row.alternate"
            else:
                style = "class:row"
            self.rows.append(_Row(row, style=style))

        super().__init__(
            children=[
                self.table_header,
                Window(height=1, char="─", style="class:header.separator"),
                *self.rows,
            ],
            window_too_small=window_too_small,
            align=align,
            padding=padding,
            padding_char=padding_char,
            padding_style=padding_style,
            width=width,
            height=height,
            z_index=z_index,
            modal=modal,
            key_bindings=key_bindings,
            style=style,
        )

    def _set_row_widths(self, width: int) -> None:
        """Set the row widths.

        Otherwise each row will decided based on their content, breaking the table.
        """
        dimensions = []
        # Get the dimensions of each column of each row in a list of lists
        for row in [self.table_header, *self.rows]:
            dimensions.append([column.preferred_width(width) for column in row.columns])

        # Transpose it so we have a list of column dimensions, so we can get the max
        # per column.
        table_width_dimensions = [
            max_layout_dimensions(list(i)) for i in zip(*dimensions)
        ]

        # Set the max dimension to the preferred
        if not self.fill_width:
            for dimension in table_width_dimensions:
                dimension.max = dimension.preferred

        # Set the widths of all elements
        for row in [self.table_header, *self.rows]:
            height = row.preferred_height(width=width, max_available_height=10000)
            for column_index in range(0, len(table_width_dimensions)):
                row.columns[column_index].width = table_width_dimensions[column_index]
                row.columns[column_index].height = height

    def write_to_screen(
        self,
        screen: Screen,
        mouse_handlers: MouseHandlers,
        write_position: WritePosition,
        parent_style: str,
        erase_bg: bool,
        z_index: Optional[int],
    ) -> None:
        """
        Render the prompt to a `Screen` instance.

        :param screen: The :class:`~prompt_toolkit.layout.screen.Screen` class
            to which the output has to be written.
        """
        self._set_row_widths(write_position.width)
        super().write_to_screen(
            screen=screen,
            mouse_handlers=mouse_handlers,
            write_position=write_position,
            parent_style=parent_style,
            erase_bg=erase_bg,
            z_index=z_index,
        )


class _Row(VSplit):
    """Define row.

    Args:
        text: text to print
    """

    def __init__(
        self,
        data: RowData,
        focusable: bool = True,
        window_too_small: Optional[Container] = None,
        align: HorizontalAlign = HorizontalAlign.LEFT,
        padding: AnyDimension = 2,
        padding_char: Optional[str] = " ",
        padding_style: str = "",
        width: AnyDimension = None,
        height: AnyDimension = None,
        z_index: Optional[int] = None,
        modal: bool = False,
        key_bindings: Optional[KeyBindingsBase] = None,
        style: Union[str, Callable[[], str]] = "class:row",
    ) -> None:
        """Initialize the widget."""
        # Define the row data
        self.data = data

        if isinstance(data, list):
            column_data = data
        elif isinstance(data, dict):
            column_data = [value for _, value in data.items()]
        elif isinstance(data, BaseModel):
            column_data = [value for _, value in data.dict().items()]

        # Define the row style
        def get_style() -> Union[str, Callable[[], str]]:
            if get_app().layout.has_focus(self):
                return f"{self.style},focused"
            else:
                return self.style

        self.columns: List[Window] = []

        for value in column_data:
            if focusable and len(self.columns) == 0:
                focusable = True
            else:
                focusable = False

            self.columns.append(
                Window(
                    FormattedTextControl(str(value), focusable=focusable),
                    style=get_style,  # type: ignore
                    always_hide_cursor=True,
                    dont_extend_height=True,
                    wrap_lines=True,
                )
            )
        super().__init__(
            children=self.columns,
            window_too_small=window_too_small,
            align=align,
            padding=padding,
            padding_char=padding_char,
            padding_style=str(style),
            width=width,
            height=height,
            z_index=z_index,
            modal=modal,
            key_bindings=key_bindings,
            style=style,
        )
