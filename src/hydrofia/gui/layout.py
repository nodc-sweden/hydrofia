"""Small helpers for building the GUI layout with a consistent look."""

import flet as ft

from hydrofia.gui import style
from hydrofia.gui.tooltip import get_tooltip_icon

# Allowed characters for numeric input fields
DECIMAL_WITH_COMMA = r"[0-9.,]"
DECIMAL = r"[0-9.]"


def card(content: ft.Control, bgcolor: str, expand: bool | int = False) -> ft.Container:
    """A coloured box with rounded corners."""
    return ft.Container(
        content=content,
        bgcolor=bgcolor,
        border_radius=style.CARD_RADIUS,
        padding=style.CARD_PADDING,
        expand=expand,
    )


def title(text: str) -> ft.Text:
    return ft.Text(text, size=style.TITLE_SIZE, weight=ft.FontWeight.W_400)


def title_with_tooltip(text: str, tooltip: str) -> ft.Row:
    return ft.Row([title(text), get_tooltip_icon(tooltip)])


def value_text(size: int | None = None) -> ft.Text:
    """Bold text used to display a calculated or loaded value."""
    return ft.Text(weight=ft.FontWeight.W_600, size=size)


def label_value(label: str, value: ft.Control) -> ft.Row:
    return ft.Row([ft.Text(label), value])


def text_field(label: str, *, allowed: str | None = None, **kwargs) -> ft.TextField:
    """Text field with the standard width. `allowed` is a regex of permitted characters."""
    if allowed is not None:
        kwargs["input_filter"] = ft.InputFilter(
            allow=True, regex_string=allowed, replacement_string=""
        )
    return ft.TextField(
        label=label, dense=style.FIELD_DENSE, width=style.FIELD_WIDTH, **kwargs
    )


def field_column(*controls: ft.Control) -> ft.Column:
    """Vertical stack of input fields."""
    return ft.Column(
        list(controls),
        alignment=ft.MainAxisAlignment.START,
        scroll=ft.ScrollMode.AUTO,
        expand=False,
        spacing=style.FIELD_COLUMN_SPACING,
    )
