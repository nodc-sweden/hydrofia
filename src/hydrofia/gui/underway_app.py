"""Small app that calculates pH for underway files and exports the results."""

import functools
import logging
from pathlib import Path

import flet as ft

from hydrofia.errors import InvalidHydrofiaFileError
from hydrofia.export_file import write_export_file
from hydrofia.gui import layout, saves, style
from hydrofia.gui.colors import Colors
from hydrofia.gui.texts import UnderwayTexts
from hydrofia.gui.tooltip import TooltipTexts
from hydrofia.underway import read_underway_file, calculate_ph_tot_labt_p0

logger = logging.getLogger(__name__)

TEXTS = UnderwayTexts()

# The window fits the card with some room to spare. The card fills the window.
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 560
WINDOW_MIN_WIDTH = 700
WINDOW_MIN_HEIGHT = 440

# Vertical space between the parts of the card
CARD_SPACING = 10
# The file lists are as high as their rows. When the card is full they scroll.
FILE_ROW_HEIGHT = 20
FILE_LIST_SPACING = 2
# Parts of the card with a fixed height. Their measured heights decide how much
# room is left for the file lists.
FIXED_PARTS = ("top", "output_directory", "result_heading", "convert")

# Keys in the saves file
INPUT_FILES = "input_files"
OUTPUT_DIRECTORY = "output_directory"

RESULT_STEM_ENDING = "_ph"
RESULT_SUFFIX = ".txt"


def get_result_path(input_path: Path, output_directory: Path) -> Path:
    """The file the conversion of the input file creates in the output directory."""
    return output_directory / f"{input_path.stem}{RESULT_STEM_ENDING}{RESULT_SUFFIX}"


def convert_underway_file(input_path: Path, result_path: Path) -> None:
    """Read the input file, calculate pH and write the result to result_path.

    For now a HydroFIA file is read and written back unchanged.
    """
    underway_data = read_underway_file(input_path)
    underway_data_with_ph = calculate_ph_tot_labt_p0(underway_data)
    write_export_file(underway_data_with_ph, result_path)


class UnderwayApp:
    def __init__(self):
        self.page: ft.Page | None = None
        self._banner: ft.Banner | None = None
        self._input_files: list[Path] = []
        self._heights: dict[str, float] = {}
        ft.run(self.main)

    def main(self, page: ft.Page):
        self.page = page
        page.title = TEXTS.title
        page.window.width = WINDOW_WIDTH
        page.window.height = WINDOW_HEIGHT
        page.window.min_width = WINDOW_MIN_WIDTH
        page.window.min_height = WINDOW_MIN_HEIGHT
        page.padding = style.PAGE_PADDING
        # FilePicker is a service in flet 1.0 and registers itself with the page.
        self._file_picker = ft.FilePicker()
        self._create_controls()
        page.add(self._build_layout())
        self._load_saved_choices()
        self._update_file_lists()

    def _create_controls(self):
        self._pick_input_files_btn = ft.Button(
            TEXTS.get_input_files_button, on_click=self._pick_input_files
        )
        self._input_file_list = _file_list()
        self._pick_output_dir_btn = ft.Button(
            TEXTS.get_output_directory_button, on_click=self._pick_output_dir
        )
        self._output_directory = layout.PathText(value=TEXTS.missing_output_directory)

        self._result_file_list = _file_list()
        self._overwrite = ft.Checkbox(value=False, active_color="red")
        self._convert_btn = ft.FilledButton(TEXTS.convert, on_click=self._convert)

    def _build_layout(self) -> ft.Control:
        self._pick_input_files_btn.width = style.PATH_BUTTON_WIDTH
        self._pick_output_dir_btn.width = style.PATH_BUTTON_WIDTH
        self._convert_btn.width = style.PATH_BUTTON_WIDTH
        top = ft.Column(
            [
                layout.card_title(
                    TEXTS.card_title,
                    TooltipTexts.underway,
                    style.INFO_DIALOG_UPPER_CARD,
                ),
                ft.Row([self._pick_input_files_btn]),
            ],
            spacing=CARD_SPACING,
        )
        output_directory = ft.Column(
            [ft.Row([self._pick_output_dir_btn]), self._output_directory],
            spacing=CARD_SPACING,
        )
        result_heading = ft.Column(
            [ft.Divider(), layout.field_label(TEXTS.create_files_label)],
            spacing=CARD_SPACING,
        )
        convert = ft.Row([self._convert_btn, self._overwrite])
        for name, part in zip(
            FIXED_PARTS, (top, output_directory, result_heading, convert), strict=True
        ):
            part.on_size_change = functools.partial(self._on_size_change, name)

        card = layout.card(
            bgcolor=Colors.hydrofia_container,
            expand=True,
            content=ft.Column(
                [
                    top,
                    self._input_file_list,
                    ft.Container(height=CARD_SPACING),
                    output_directory,
                    ft.Container(expand=True),
                    result_heading,
                    self._result_file_list,
                    convert,
                ],
                spacing=CARD_SPACING,
            ),
        )
        card.on_size_change = functools.partial(self._on_size_change, "card")
        return card

    # ------------------------------------------------------------------
    # Pickers
    # ------------------------------------------------------------------
    async def _pick_input_files(self, e=None):
        files = await self._file_picker.pick_files(
            dialog_title=TEXTS.dialog_title_input_files,
            initial_directory=_existing_directory(*self._input_files),
            allow_multiple=True,
        )
        if not files:
            return
        self._close_banner()

        for file in files:
            try:
                read_underway_file(file.path)
            except InvalidHydrofiaFileError:
                self._show_info(TEXTS.invalid_underway_file(file.path))
                return

        self._input_files = sorted(Path(f.path) for f in files)
        self._update_file_lists()

    async def _pick_output_dir(self, e=None):
        path = await self._file_picker.get_directory_path(
            dialog_title=TEXTS.dialog_title_output_directory,
            initial_directory=_existing_directory(
                self.output_directory, *self._input_files
            ),
        )
        if not path:
            return
        self._close_banner()
        self._output_directory.value = path
        self._output_directory.update()
        self._update_file_lists()

    # ------------------------------------------------------------------
    # Saved choices
    # ------------------------------------------------------------------
    def _load_saved_choices(self):
        """Show the choices of the latest conversion. Paths that are gone are left out."""
        data = saves.load_values(saves.UNDERWAY_SAVES_PATH)
        output_directory = data.get(OUTPUT_DIRECTORY)
        if output_directory and Path(output_directory).is_dir():
            self._output_directory.value = output_directory
            self._output_directory.update()

    def _save_choices(self):
        data = {
            #INPUT_FILES: [str(path) for path in self._input_files],
            OUTPUT_DIRECTORY: str(self.output_directory),
        }
        try:
            saves.save_values(saves.UNDERWAY_SAVES_PATH, data)
        except OSError:
            logger.exception("Could not save the latest choices")

    # ------------------------------------------------------------------
    # File lists
    # ------------------------------------------------------------------
    def _update_file_lists(self):
        """Show the chosen files and the files to create.

        Offer to overwrite if any of the files to create exist.
        """
        _show_paths(self._input_file_list, self._input_files, TEXTS.missing_input_files)
        result_paths = self.result_paths
        _show_paths(self._result_file_list, result_paths, TEXTS.missing_result_path)
        self._fit_file_lists()

        nr_existing = sum(path.exists() for path in result_paths)
        self._overwrite.visible = nr_existing > 0
        self._overwrite.value = False
        self._overwrite.label = TEXTS.files_exist(nr_existing)
        self._overwrite.update()

    def _on_size_change(self, name: str, e: ft.LayoutSizeChangeEvent):
        self._heights[name] = e.height
        self._fit_file_lists()

    def _fit_file_lists(self):
        """Make each file list as high as its rows, or share the room left if less."""
        if any(name not in self._heights for name in ("card", *FIXED_PARTS)):
            return
        nr_gaps = 6  # between the seven parts of the card
        room = (
            self._heights["card"]
            - 2 * style.CARD_PADDING
            - sum(self._heights[name] for name in FIXED_PARTS)
            - nr_gaps * CARD_SPACING
            - 1  # margin for rounding, so the content never overflows
        )
        heights = _share_height(
            _list_height(self._input_file_list),
            _list_height(self._result_file_list),
            max(room, 0),
        )
        for file_list, height in zip(
            (self._input_file_list, self._result_file_list), heights, strict=True
        ):
            if file_list.height != height:
                file_list.height = height
                file_list.update()

    # ------------------------------------------------------------------
    # Convert
    # ------------------------------------------------------------------
    def _convert(self, e=None):
        error = self._get_input_error()
        if error:
            self._show_info(error)
            return
        pairs = list(zip(self._input_files, self.result_paths, strict=True))
        self._set_controls_disabled(True)
        try:
            for nr, (input_path, result_path) in enumerate(pairs, start=1):
                self._show_info(
                    TEXTS.converting(nr, len(pairs), input_path.name), status="working"
                )
                try:
                    convert_underway_file(input_path, result_path)
                except Exception as exc:
                    logger.exception("Conversion of %s failed", input_path)
                    self._show_info(TEXTS.convert_failed(input_path.name, nr - 1, exc))
                    return
        finally:
            self._set_controls_disabled(False)
            self._update_file_lists()
        self._save_choices()
        self._show_info(TEXTS.converted(len(pairs), self.output_directory), "good")

    def _get_input_error(self) -> str | None:
        missing = [path for path in self._input_files if not path.is_file()]
        result_paths = self.result_paths
        error = None
        if not self._input_files:
            error = TEXTS.missing_input_files
        elif missing:
            error = TEXTS.non_existing_input_file(missing[0])
        elif not self.output_directory:
            error = TEXTS.missing_output_directory
        elif not self.output_directory.is_dir():
            error = TEXTS.non_existing_output_directory
        elif len(set(result_paths)) < len(result_paths):
            error = TEXTS.duplicate_result_paths
        elif any(path.exists() for path in result_paths) and not self._overwrite.value:
            error = TEXTS.select_overwrite_files
        return error

    def _set_controls_disabled(self, disabled: bool):
        for control in (
            self._pick_input_files_btn,
            self._pick_output_dir_btn,
            self._overwrite,
            self._convert_btn,
        ):
            control.disabled = disabled
            control.update()

    # ------------------------------------------------------------------
    # Banner
    # ------------------------------------------------------------------
    def _show_info(self, text: str, status: str = "bad"):
        self._close_banner()
        self._banner = ft.Banner(
            bgcolor=Colors.banner(status),
            leading=ft.Icon(
                ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER, size=40
            ),
            content=ft.Column([ft.Text(text)]),
            force_actions_below=True,
            actions=[ft.TextButton("OK!", on_click=self._close_banner)],
        )
        self.page.show_dialog(self._banner)

    def _close_banner(self, e=None):
        if self._banner is None or not self._banner.open:
            return
        self._banner.open = False
        self._banner.update()

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------
    @property
    def output_directory(self) -> Path | None:
        value = self._output_directory.value
        if not value or value == TEXTS.missing_output_directory:
            return None
        return Path(value)

    @property
    def result_paths(self) -> list[Path]:
        if not self.output_directory:
            return []
        return [
            get_result_path(path, self.output_directory) for path in self._input_files
        ]


def _file_list() -> ft.Column:
    """List of paths. The height is set to fit the card, it scrolls when needed."""
    return ft.Column(spacing=FILE_LIST_SPACING, scroll=ft.ScrollMode.AUTO)


def _show_paths(file_list: ft.Column, paths: list[Path], missing_text: str):
    if paths:
        file_list.controls = [_path_row(str(path), is_file=True) for path in paths]
    else:
        file_list.controls = [_path_row(missing_text)]
    # Until the card is measured, show all rows
    file_list.height = _list_height(file_list)
    file_list.update()


def _path_row(value: str, is_file: bool = False) -> layout.PathText:
    return layout.PathText(
        value=value,
        is_file=is_file,
        height=FILE_ROW_HEIGHT,
        alignment=ft.Alignment.CENTER_LEFT,
    )


def _list_height(file_list: ft.Column) -> float:
    """Height of all rows in the list."""
    nr_rows = len(file_list.controls)
    return nr_rows * FILE_ROW_HEIGHT + max(nr_rows - 1, 0) * FILE_LIST_SPACING


def _share_height(first: float, second: float, room: float) -> tuple[float, float]:
    """Heights for two lists that need first and second but together get room.

    A list that needs less than half of the room gets what it needs and the other
    list gets the rest.
    """
    if first + second <= room:
        return first, second
    half = room / 2
    if first <= half:
        return first, room - first
    if second <= half:
        return room - second, second
    return half, half


def _existing_directory(*paths: Path | None) -> str | None:
    """The first existing directory among the paths, or the folder of a file."""
    for path in paths:
        if not path:
            continue
        directory = path if path.is_dir() else path.parent
        if directory.is_dir():
            return str(directory)
    return None


def main(log_in_console) -> None:
    """Entry point for the console script."""
    logging.basicConfig(level=log_in_console)
    UnderwayApp()


def run() -> None:
    """Entry point for the console script."""
    main(log_in_console="INFO")
