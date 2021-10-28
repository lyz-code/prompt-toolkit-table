"""Define the Table widget."""

from typing import TYPE_CHECKING, List, Optional

from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.margins import ConditionalMargin, ScrollbarMargin

from .control import TableControl, TableData

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyBindingsBase


class Table:
    """Define the widget to show the data rows."""

    container_style: str = ""
    default_style: str = ""
    selected_style: str = ""
    show_scrollbar: bool = True

    def __init__(
        self,
        data: "TableData",
        header: Optional[List[str]] = None,
        key_bindings: Optional["KeyBindingsBase"] = None,
    ) -> None:
        """Initialize the table buffer."""
        self.header = header
        self._selected_index = 0

        # Control and window.
        self.control = TableControl(data, key_bindings=key_bindings, focusable=True)

        self.window = Window(
            content=self.control,
            style=self.container_style,
            right_margins=[
                ConditionalMargin(
                    margin=ScrollbarMargin(display_arrows=False),
                    filter=Condition(lambda: self.show_scrollbar),
                ),
            ],
            dont_extend_height=True,
        )

    def __pt_container__(self) -> Window:
        """Define the widget method."""
        return self.window
