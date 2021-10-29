"""Define the Table widget."""

from typing import TYPE_CHECKING, List, Optional

from prompt_toolkit.application import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.margins import ConditionalMargin, ScrollbarMargin
from prompt_toolkit.widgets import Label

from prompt_toolkit_table.control import StyleAndTextTuples

from .control import TableControl, TableData

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyBindingsBase


class Table:
    """Define the widget to show the data rows."""

    container_style: str = ""
    default_style: str = ""
    selected_style: str = ""
    show_scrollbar: bool = True
    show_header: bool = True

    def __init__(
        self,
        data: "TableData",
        header: Optional[List[str]] = None,
        key_bindings: Optional["KeyBindingsBase"] = None,
    ) -> None:
        """Initialize the table buffer."""
        self.header = header
        self._initial_header_draw = False
        self._initial_separator_draw = False

        # Control and window.
        self.control = TableControl(data, key_bindings=key_bindings, focusable=True)
        self.control.create_text()

        self.window = HSplit(
            [
                Label(self._update_header),
                Label(self._update_separator),
                Window(
                    content=self.control,
                    style=self.container_style,
                    right_margins=[
                        ConditionalMargin(
                            margin=ScrollbarMargin(display_arrows=False),
                            filter=Condition(lambda: self.show_scrollbar),
                        ),
                    ],
                    dont_extend_height=True,
                ),
            ]
        )

    def _update_header(self) -> "StyleAndTextTuples":
        """Get the value of the component from the control.

        The control sets the header and separator, when the window is resized, they
        need to get the updated version from the control.
        We need to get the initial size on the first run otherwise the it doesn't
        match the content
        """
        if not self._initial_header_draw:
            initial_width = get_app().output.get_size().columns
            self.control.create_text(initial_width)
            self._initial_header_draw = True

        return self.control.header_text

    def _update_separator(self) -> "StyleAndTextTuples":
        """Get the value of the component from the control.

        The control sets the header and separator, when the window is resized, they
        need to get the updated version from the control.

        We need to get the initial size on the first run otherwise the it doesn't
        match the content
        """
        if not self._initial_separator_draw:
            initial_width = get_app().output.get_size().columns
            self.control.create_text(initial_width)
            self._initial_separator_draw = True
        return self.control.separator_text

    def __pt_container__(self) -> HSplit:
        """Define the widget method."""
        return self.window
