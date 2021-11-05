"""Demo of the package."""

from typing import List, Optional

from faker import Faker
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.output.color_depth import ColorDepth
from pydantic import BaseModel, Field

from prompt_toolkit_table import TABLE_STYLE
from prompt_toolkit_table.widgets import Table


class User(BaseModel):
    """Define the example of a model."""

    id_: int = Field(0, title="ID")
    name: str = "Jane Doe"
    bio: Optional[str] = None


def create_user_data() -> List[User]:
    """Create fake list data."""
    faker = Faker()

    return [
        User(id_=faker.pyint(), name=faker.paragraph(), bio=faker.name())
        for _ in range(0, 200)
    ]


def main() -> None:
    """Run the demo."""
    data = create_user_data()

    table = Table(data, show_scrollbar=False)

    # Key bindings

    kb = KeyBindings()

    @kb.add("c-c", eager=True)
    @kb.add("q", eager=True)
    def exit_(event: KeyPressEvent) -> None:
        """Exit the user interface."""
        event.app.exit()

    app = Application(  # type: ignore
        layout=Layout(table),
        full_screen=True,
        key_bindings=kb,
        style=TABLE_STYLE,
        color_depth=ColorDepth.DEPTH_24_BIT,
    )

    app.run()


if __name__ == "__main__":
    main()
