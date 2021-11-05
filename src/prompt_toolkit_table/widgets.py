"""Define the Table widget."""

from typing import TYPE_CHECKING, List, Optional

from prompt_toolkit.application import get_app
from prompt_toolkit.filters.utils import to_filter
from prompt_toolkit.layout import ConditionalContainer
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.margins import ConditionalMargin, ScrollbarMargin
from prompt_toolkit.widgets import Label

from prompt_toolkit_table.model import StyleAndTextTuples

from .control import TableControl, TableData

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyBindingsBase


class Table:
    """Define the widget to show the data rows."""

    def __init__(
        self,
        data: "TableData",
        header: Optional[List[str]] = None,
        key_bindings: Optional["KeyBindingsBase"] = None,
        show_header: bool = True,
        show_scrollbar: bool = True,
        container_style: str = "",
    ) -> None:
        """Initialize the table buffer."""
        self.header = header
        self.key_bindings = key_bindings
        self.show_header = show_header
        self.show_scrollbar = show_scrollbar
        self.container_style = container_style
        self._initial_header_draw = False
        self._initial_separator_draw = False

        # Control and window.
        self.control = TableControl(data, key_bindings=key_bindings, focusable=True)
        self.control.create_content()

        self.window = HSplit(
            [
                ConditionalContainer(
                    Label(self._update_header), filter=to_filter(self.show_header)
                ),
                Window(
                    content=self.control,
                    style=self.container_style,
                    right_margins=[
                        ConditionalMargin(
                            margin=ScrollbarMargin(display_arrows=False),
                            filter=to_filter(self.show_scrollbar),
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
        We need to get the initial size on the first run otherwise it doesn't
        match the content
        """
        if not self._initial_header_draw:
            initial_width = get_app().output.get_size().columns
            self.control.create_content(initial_width)
            self._initial_header_draw = True

        return self.control.header_text

    def __pt_container__(self) -> HSplit:
        """Define the widget method."""
        return self.window
