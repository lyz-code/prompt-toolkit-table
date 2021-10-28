"""Define the Table styles."""

from prompt_toolkit.styles import Style

# Styles

TABLE_STYLE = Style(
    [
        ("row", "bg:#002b36 #657b83"),
        ("focused", "bg:#657b83 #002b36"),
        ("row.alternate", "bg:#073642"),
        ("header", "bg:#002b36 #6c71c4"),
        ("header.separator", "#657b83"),
        ("scrollbar.background", "bg:#002b36"),
        ("scrollbar.button", "bg:#657b83"),
    ]
)
