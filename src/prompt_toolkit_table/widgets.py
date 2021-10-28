"""Define the Table widget."""

from typing import TYPE_CHECKING, List, Optional

from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import to_formatted_text
from prompt_toolkit.formatted_text.utils import fragment_list_to_text
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.margins import ConditionalMargin, ScrollbarMargin

from .control import TableControl

if TYPE_CHECKING:
    from .control import TableData


class Table:
    """Define the widget to show the data rows."""

    container_style: str = ""
    default_style: str = ""
    selected_style: str = ""
    show_scrollbar: bool = True

    def __init__(self, values: "TableData", header: Optional[List[str]] = None) -> None:
        """Initialize the table buffer."""
        assert len(values) > 0

        self.header = header
        self.values = values
        self._selected_index = 0

        # Key bindings.
        kb = KeyBindings()

        @kb.add("k")
        @kb.add("up")
        def _up(event: KeyPressEvent) -> None:
            self._selected_index = max(0, self._selected_index - 1)

        @kb.add("j")
        @kb.add("down")
        def _down(event: KeyPressEvent) -> None:
            self._selected_index = min(len(self.values) - 1, self._selected_index + 1)

        @kb.add("c-u")
        @kb.add("pageup")
        def _pageup(event: KeyPressEvent) -> None:
            window = event.app.layout.current_window
            if window.render_info:
                self._selected_index = max(
                    0, self._selected_index - len(window.render_info.displayed_lines)
                )

        @kb.add("c-d")
        @kb.add("pagedown")
        def _pagedown(event: KeyPressEvent) -> None:
            window = event.app.layout.current_window
            if window.render_info:
                self._selected_index = min(
                    len(self.values) - 1,
                    self._selected_index + len(window.render_info.displayed_lines),
                )

        @kb.add("enter")
        @kb.add(" ")
        def _click(event: KeyPressEvent) -> None:
            self._handle_enter()

        @kb.add(Keys.Any)
        def _find(event: KeyPressEvent) -> None:
            # We first check values after the selected value, then all values.
            values = list(self.values)
            # E203: whitespace before ':' -> Black introduces it :S
            for value in values[self._selected_index + 1 :] + values:  # noqa: E203
                text = fragment_list_to_text(to_formatted_text(value)).lower()

                if text.startswith(event.data.lower()):
                    self._selected_index = self.values.index(value)
                    return

        # Control and window.
        self.control = TableControl(values, key_bindings=kb, focusable=True)

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

    def _handle_enter(self) -> None:
        """Select the value under the cursor."""
        self.current_value = self.values[self._selected_index]

    def __pt_container__(self) -> Window:
        """Define the widget method."""
        return self.window
