"""Small helpers for building the GUI layout with a consistent look."""

import pathlib

import flet as ft

from hydrofia.gui import style
from hydrofia.gui.colors import Colors
from hydrofia.gui.tooltip import get_info_button

# Patterns for numeric input fields. Flet tests the whole field content against the
# pattern and rejects the edit on no match, so they must be anchored and match "".
DECIMAL_WITH_COMMA = r"^[0-9.,]*$"
DECIMAL = r"^[0-9.]*$"


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
    """Heading for a part of the page."""
    return ft.Text(text, size=style.TITLE_SIZE, weight=ft.FontWeight.W_600)


def title_with_info(text: str, tooltip: str, dialog_alignment: ft.Alignment) -> ft.Row:
    """Heading for a part of the page, with an info button."""
    return ft.Row([title(text), get_info_button(text, tooltip, dialog_alignment)])


def card_title(text: str, tooltip: str, dialog_alignment: ft.Alignment) -> ft.Container:
    """Main heading of a card, with an info button and space below it."""
    heading = ft.Text(text, size=style.CARD_TITLE_SIZE, weight=ft.FontWeight.W_600)
    return ft.Container(
        content=ft.Row([heading, get_info_button(text, tooltip, dialog_alignment)]),
        padding=ft.Padding.only(bottom=style.CARD_TITLE_BOTTOM_PADDING),
    )


@ft.control
class PathText(ft.Container):
    """Read-only text showing a path, or a message when the value is not a path.

    In a file path the folder is subdued and the file name is emphasized.
    """

    value: str = ""
    is_file: bool = False

    def init(self):
        self.content = ft.Text(size=style.PATH_TEXT_SIZE, spans=self._get_spans())

    def before_update(self):
        super().before_update()
        self.content.spans = self._get_spans()

    def _get_spans(self) -> list[ft.TextSpan]:
        path = pathlib.Path(self.value)
        if not self.is_file or not self.value or not path.is_absolute():
            # A blank span keeps the height of the row when there is no value.
            return [_path_span(self.value or " ", Colors.path_text)]
        folder = self.value[: -len(path.name)]
        return [
            _path_span(folder, Colors.path_folder),
            _path_span(path.name, Colors.path_text, weight=ft.FontWeight.W_600),
        ]


def _path_span(
    text: str, color: str, weight: ft.FontWeight | None = None
) -> ft.TextSpan:
    return ft.TextSpan(text, style=ft.TextStyle(color=color, weight=weight))


def value_text(size: int | None = None) -> ft.Text:
    """Bold text used to display a calculated or loaded value."""
    return ft.Text(weight=ft.FontWeight.W_600, size=size)


def label_value(label: str, value: ft.Control) -> ft.Row:
    return ft.Row([ft.Text(label), value])


def path_row(button: ft.Button, path: PathText, *extras: ft.Control) -> ft.Row:
    """A picker button of standard width followed by the path it selected."""
    button.width = style.PATH_BUTTON_WIDTH
    path.expand = True
    return ft.Row([button, path, *extras])


def field_label(text: str) -> ft.Text:
    """Bold label for a group of controls or a value below it."""
    return ft.Text(text, weight=ft.FontWeight.W_600)


def labeled_row(label: str, *controls: ft.Control) -> ft.Container:
    """A row of controls below a label, set apart from the content above."""
    return ft.Container(
        content=ft.Column(
            [field_label(label), ft.Row(list(controls))],
            spacing=style.LABELED_ROW_SPACING,
        ),
        padding=ft.Padding.only(top=style.LABELED_ROW_TOP_PADDING),
    )


def output_row(
    button: ft.Button,
    label: str,
    path: PathText,
    overwrite: ft.Checkbox,
    open_button: ft.Button | None = None,
) -> ft.Column:
    """The file to create, with its create button below and open button to the right."""
    button.width = style.PATH_BUTTON_WIDTH
    controls = [button, overwrite]
    if open_button is not None:
        controls += [ft.Container(expand=True), open_button]
    return ft.Column(
        [
            ft.Column(
                [field_label(label), path],
                spacing=style.OUTPUT_LABEL_SPACING,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            ft.Row(controls),
        ]
    )


def text_field(label: str, *, allowed: str | None = None, **kwargs) -> ft.TextField:
    """Text field with the standard width. `allowed` is a regex for the whole content."""
    if allowed is not None:
        kwargs["input_filter"] = ft.InputFilter(
            allow=True, regex_string=allowed, replacement_string=""
        )
    return ft.TextField(
        label=label, dense=style.FIELD_DENSE, width=style.FIELD_WIDTH, **kwargs
    )


def float_field(label: str, **kwargs) -> ft.TextField:
    """Text field restricted to characters used in decimal numbers."""
    return text_field(label, allowed=DECIMAL_WITH_COMMA, **kwargs)


def parse_float(text: str) -> float | None:
    """Return the value of a decimal string with point or comma, or None if invalid."""
    try:
        return float(text.strip().replace(",", "."))
    except ValueError:
        return None


def field_column(*controls: ft.Control) -> ft.Column:
    """Vertical stack of input fields."""
    return ft.Column(
        list(controls),
        alignment=ft.MainAxisAlignment.START,
        scroll=ft.ScrollMode.AUTO,
        expand=False,
        spacing=style.FIELD_COLUMN_SPACING,
    )
