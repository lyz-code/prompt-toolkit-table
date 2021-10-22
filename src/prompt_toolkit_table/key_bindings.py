"""Define the key bindings."""

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.layout import Layout

# Table Key bindings

table_bindings = KeyBindings()


@table_bindings.add("k")
@table_bindings.add("up")
def _up(event: KeyPressEvent) -> None:
    layout = event.app.layout
    if _locate_focused_window(layout) > 0:
        focus_previous(event)


@table_bindings.add("j")
@table_bindings.add("down")
def _down(event: KeyPressEvent) -> None:
    layout = event.app.layout
    if _locate_focused_window(layout) < len(layout.get_visible_focusable_windows()) - 1:
        focus_next(event)


@table_bindings.add("c-u")
@table_bindings.add("pageup")
def _pageup(event: KeyPressEvent) -> None:
    layout = event.app.layout
    window_index = _locate_focused_window(layout)
    if window_index > 0:
        layout.focus(layout.get_visible_focusable_windows()[max(0, window_index - 10)])


@table_bindings.add("c-d")
@table_bindings.add("pagedown")
def _pagedown(event: KeyPressEvent) -> None:
    layout = event.app.layout
    window_index = _locate_focused_window(layout)
    num_windows = len(layout.get_visible_focusable_windows())
    if window_index < num_windows - 1:
        layout.focus(
            layout.get_visible_focusable_windows()[
                min(num_windows - 1, window_index + 10)
            ]
        )


def _locate_focused_window(layout: Layout) -> int:
    """Locate the focused window against the rest."""
    return layout.get_visible_focusable_windows().index(layout.current_window)
