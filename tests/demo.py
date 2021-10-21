"""Demo of the package."""

from typing import List, Optional

from faker import Faker
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.styles import Style
from pydantic import BaseModel, Field

from prompt_toolkit_table import Table


class User(BaseModel):
    """Define the example of a model."""

    id_: int = Field(0, title="ID")
    name: str = "Jane Doe"
    bio: Optional[str] = None


def create_user_data() -> List[User]:
    """Create fake list data."""
    faker = Faker()

    return [
        User(id_=faker.pyint(), name=faker.name(), bio=faker.sentence())
        for _ in range(0, 10)
    ]


data = create_user_data()

table = Table(data, fill_width=True)

# Key bindings

kb = KeyBindings()


@kb.add("c-c", eager=True)
@kb.add("q", eager=True)
def exit_(event: KeyPressEvent) -> None:
    """Exit the user interface."""
    event.app.exit()


style = Style(
    [
        ("row", "bg:#002b36 #657b83"),
        ("focused", "#268bd2"),
        ("row.alternate", "bg:#073642"),
        ("header", "bg:#002b36 #6c71c4"),
        ("header.separator", "#657b83"),
    ]
)

app = Application(  # type: ignore
    layout=Layout(table),
    full_screen=True,
    key_bindings=kb,
    style=style,
    color_depth=ColorDepth.DEPTH_24_BIT,
)

app.run()
