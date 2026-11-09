import asyncio
import contextlib
import json
import logging.handlers
import pathlib
import re
import sys

import flet as ft

import hydrofia
from hydrofia import reference_batch, utils
from hydrofia.errors import InvalidBatchError, InvalidHydrofiaFileError
from hydrofia.gui import layout, saves, style
from hydrofia.gui.colors import Colors
from hydrofia.gui.texts import Texts
from hydrofia.gui.tooltip import TooltipTexts
from hydrofia.tris_calculations import TRIS_BUFFERS

logger = logging.getLogger(__name__)

if getattr(sys, "frozen", False):
    DIRECTORY = pathlib.Path(sys.executable).parent
else:
    DIRECTORY = pathlib.Path(__file__).parent

TOOLTIP_TEXT = TooltipTexts()

TEXTS = Texts()
COLORS = Colors()

# Time for the text field's own Delete edit to reach Python before the field is cleared
DELETE_SETTLE_SECONDS = 0.1

TEMPLATE_STEM_ENDING = "_rättningsfil"
RESULT_STEM_ENDING = "_resultat"

DEFAULT_DEPTH_MARGINS = {"meta_surface": 4.0, "meta_bottom": 4.0, "meta_diff": 1.0}


def get_config():
    path = DIRECTORY / "config.json"
    if not path.exists():
        return {}
    with path.open() as fid:
        return json.load(fid)


class FletApp:
    def __init__(self, log_in_console=False):
        self._log_in_console = log_in_console
        self.page = None
        self.file_picker = None
        self._config = {}
        self._attributes = {}
        self._progress_bars = {}
        self._progress_texts = {}
        self._instrument_items = {}
        self._current_source_instrument = None

        self._batches = reference_batch.get_latest_batches()

        self._month_all_option = "ALLA"
        self._periods: dict[int, list[int]] = {}

        self._toggle_buttons: list[ft.LayoutControl] = []  # set in _create_controls

        self.logging_level = "DEBUG"
        self.logging_format = (
            "%(asctime)s [%(levelname)10s]    "
            "%(pathname)s [%(lineno)d] => %(funcName)s():    %(message)s"
        )
        self.logging_format_stdout = (
            "[%(levelname)10s] %(filename)s: %(funcName)s() [%(lineno)d] %(message)s"
        )
        self._setup_logger()

        self.app = ft.run(self.main)

    @property
    def _log_directory(self):
        path = pathlib.Path(pathlib.Path.home(), "logs")
        path.mkdir(parents=True, exist_ok=True)
        return path

    def main(self, page: ft.Page):
        self.page = page
        self.page.title = TEXTS.title
        self.page.window.maximized = True
        self.page.padding = style.PAGE_PADDING
        self.page.on_resize = self._fit_content_to_window
        self._initiate_pickers()
        self._build()
        self.page.on_keyboard_event = self._on_keyboard_event
        self._initiate_banner()

        saves.add_control("_hydrofia_file_path", self._hydrofia_file_path)
        saves.add_control("_template_directory", self._template_directory)
        saves.add_control("_use_template_path", self._use_template_path)
        saves.add_control("_ctd_directory", self._ctd_directory)
        saves.add_control("_metadata_signature", self._metadata_signature)
        saves.add_control("_metadata_project", self._metadata_project)
        saves.add_control("_batch_nr", self._batch_nr)

        saves.load(self)

        self._check_paths()

        self._update_period_options()
        self._update_create_template_path()
        self._update_create_result_path()

        self._check_use_template_path()

        self._update_batch_info()

        self._reset_depth_margins()

        self._fit_content_to_window()

    def _fit_content_to_window(self, *args):
        """Let the content fill the window, or scroll it when the window is too low."""
        if self.page.height is None:
            return
        too_low = self.page.height < style.MIN_PAGE_HEIGHT
        self._content.expand = not too_low
        self._content.height = (
            style.MIN_PAGE_HEIGHT - 2 * style.PAGE_PADDING if too_low else None
        )
        self.page.scroll = ft.ScrollMode.AUTO if too_low else None
        self.page.update()

    def _check_paths(self):
        """Show the missing text for all paths that are not set or no longer exist"""
        for widget, missing_text in [
            (self._hydrofia_file_path, TEXTS.missing_hydrofia_file_path),
            (self._template_directory, TEXTS.missing_template_directory),
            (self._use_template_path, TEXTS.missing_use_template_path),
            (self._ctd_directory, TEXTS.missing_ctd_directory),
        ]:
            if widget.value.strip() and pathlib.Path(widget.value).exists():
                continue
            widget.value = missing_text
            widget.update()

    def update_page(self):
        self.page.update()

    def _setup_logger(self, **kwargs):
        name = "hydrofia"
        # self.logger = logging.getLogger(name)
        self.logger = logging.getLogger()
        self.logger.setLevel(self.logging_level)

        debug_file_path = pathlib.Path(self._log_directory, f"{name}_debug.log")
        handler = logging.handlers.TimedRotatingFileHandler(
            str(debug_file_path), when="H", interval=3, backupCount=10
        )
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(self.logging_format)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        debug_file_path = pathlib.Path(self._log_directory, f"{name}_warning.log")
        handler = logging.handlers.TimedRotatingFileHandler(
            str(debug_file_path), when="D", interval=1, backupCount=14
        )
        handler.setLevel(logging.WARNING)
        formatter = logging.Formatter(self.logging_format)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        if self._log_in_console:
            handler = logging.StreamHandler()
            handler.setLevel(self._log_in_console)
            formatter = logging.Formatter(self.logging_format)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _initiate_pickers(self):
        # FilePicker is a service in flet 1.0 and registers itself with the current page.
        self._file_picker = ft.FilePicker()

    @staticmethod
    def _get_start_directory(*paths: pathlib.Path | None) -> str | None:
        """Return the first existing directory among the paths, or the folder of a file.

        With None the file dialog falls back to the default of the operating system.
        """
        for path in paths:
            if not path:
                continue
            directory = path if path.is_dir() else path.parent
            if directory.is_dir():
                return str(directory)
        return None

    async def _pick_hydrofia_file(self, e=None):
        files = await self._file_picker.pick_files(
            dialog_title=TEXTS.dialog_title_hydrofia_file_path,
            initial_directory=self._get_start_directory(self.hydrofia_file_path),
            allowed_extensions=["txt"],
            allow_multiple=False,
        )
        self._on_pick_hydrofia_file_path(files)

    async def _pick_template_dir(self, e=None):
        path = await self._file_picker.get_directory_path(
            dialog_title=TEXTS.dialog_title_template_directory,
            initial_directory=self._get_start_directory(self.template_directory),
        )
        self._on_pick_template_dir(path)

    async def _pick_ctd_dir(self, e=None):
        path = await self._file_picker.get_directory_path(
            dialog_title=TEXTS.dialog_title_ctd_directory,
            initial_directory=self._get_start_directory(self.ctd_directory),
        )
        self._on_pick_ctd_dir(path)

    async def _pick_template_file(self, e=None):
        files = await self._file_picker.pick_files(
            dialog_title=TEXTS.dialog_title_template_file,
            initial_directory=self._get_start_directory(
                self.use_template_path, self.template_directory
            ),
            allowed_extensions=["xlsx"],
            allow_multiple=False,
        )
        self._on_pick_template_file(files)

    def _initiate_banner(self):
        # Banner is a dialog in flet 1.0; a new one is created each time info is shown.
        self._banner: ft.Banner | None = None

    def _create_banner(self, text, color):
        return ft.Banner(
            bgcolor=color,
            leading=ft.Icon(
                ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER, size=40
            ),
            content=ft.Column([ft.Text(text)]),
            force_actions_below=True,
            actions=[
                ft.TextButton("OK!", on_click=self._close_banner),
            ],
        )

    def _disable_toggle_buttons(self):
        for btn in self._toggle_buttons:
            btn.disabled = True
            btn.update()

    def _enable_toggle_buttons(self):
        for btn in self._toggle_buttons:
            btn.disabled = False
            btn.update()

    def _close_banner(self, e=None):
        if self._banner is None or not self._banner.open:
            return
        self._banner.open = False
        self._banner.update()

    def _show_info(self, text, status="bad"):
        self._close_banner()
        self._banner = self._create_banner(text, COLORS.banner(status))
        self.page.show_dialog(self._banner)

    def _build(self):
        self._create_controls()
        self.page.controls.extend(self._build_layout())

        self._open_template_file_btn.visible = False
        self._open_result_file_btn.visible = False

        self.update_page()

    # ------------------------------------------------------------------
    # Controls: created here, placed in _build_layout()
    # ------------------------------------------------------------------
    def _create_controls(self):
        self._create_tris_controls()
        self._create_batch_controls()
        self._create_template_controls()
        self._create_result_controls()
        self._track_float_field_focus(
            self._tris_temp,
            self._tris_measured_ph,
            self._batch_temp,
            self._batch_measured_ph,
        )

        # Disabled while a template or result file is being created
        self._toggle_buttons = [
            self._pick_hydrofia_file_btn,
            self._pick_template_dir_btn,
            self._overwrite_template,
            self._open_template_file_btn,
            self._open_result_file_btn,
            self._pick_template_file_btn,
            self._pick_ctd_dir_btn,
        ]

    def _track_float_field_focus(self, *fields: ft.TextField):
        self._focused_float_field = None
        for field in fields:
            field.on_focus = self._on_float_field_focus
            field.on_blur = self._on_float_field_blur

    def _on_float_field_focus(self, e):
        self._focused_float_field = e.control

    def _on_float_field_blur(self, e):
        if self._focused_float_field is e.control:
            self._focused_float_field = None

    async def _on_keyboard_event(self, e: ft.KeyboardEvent):
        """Clear the focused float field when Delete is pressed."""
        field = self._focused_float_field
        if field is None or e.key != "Delete":
            return
        await asyncio.sleep(DELETE_SETTLE_SECONDS)
        field.value = ""
        field.update()
        if field.on_change:
            field.on_change(e)

    def _create_tris_controls(self):
        self._tris_type = ft.Dropdown(
            label="TRIS-buffert",
            value="TRIS_Dickson",
            options=[ft.DropdownOption(item) for item in TRIS_BUFFERS],
            on_select=self._update_tris_ph,
            dense=True,
        )

        self._tris_ph = layout.value_text()
        self._tris_plot_value = layout.value_text(size=style.HIGHLIGHT_SIZE)

        self._tris_temp = layout.float_field(
            TEXTS.temperature,
            on_change=self._update_tris_ph,
        )
        self._tris_measured_ph = layout.float_field(
            TEXTS.measured_ph,
            on_change=self._update_tris_ph,
        )

    def _create_batch_controls(self):
        """Step 1: pH of the reference batch (CRM)"""
        self._batch_nr = ft.Dropdown(
            label="Batchnummer",
            hint_text="Använd data från batch nummer...",
            options=[
                ft.DropdownOption(item) for item in reversed(self._batches.batch_nr_list)
            ],
            on_select=self._on_select_batch,
            dense=True,
        )
        self._batch_nr.value = str(self._batches.latest_batch_nr)

        self._batch_alk = layout.value_text()
        self._batch_dic = layout.value_text()
        self._batch_salt = layout.value_text()
        self._batch_ph = layout.value_text()
        self._batch_plot_value = layout.value_text(size=style.HIGHLIGHT_SIZE)

        self._batch_temp = layout.float_field(
            TEXTS.temperature,
            on_change=self._update_crm_ph,
        )
        self._batch_measured_ph = layout.float_field(
            TEXTS.measured_ph,
            on_change=self._update_crm_ph,
        )

    def _create_template_controls(self):
        """Step 2: create the template (rättningsfil) from a HydroFIA export"""
        self._metadata_signature = layout.text_field(TEXTS.signature)
        self._metadata_project = layout.text_field(
            TEXTS.project, on_blur=self._update_create_template_path
        )

        self._pick_hydrofia_file_btn = ft.Button(
            TEXTS.get_hydrofia_export_button, on_click=self._pick_hydrofia_file
        )
        self._hydrofia_file_path = layout.PathText(
            value=TEXTS.missing_hydrofia_file_path, is_file=True
        )

        self._year = ft.Dropdown(
            label="År",
            hint_text="Filtrera på år",
            on_select=self._on_select_year,
            dense=True,
        )

        self._month = ft.Dropdown(
            label="Månad",
            hint_text="Filtrera på månad",
            options=[ft.DropdownOption(self._month_all_option)],
            on_select=self._update_create_template_path,
            autofocus=True,
            dense=True,
        )
        self._month.value = self._month_all_option

        self._pick_template_dir_btn = ft.Button(
            TEXTS.get_template_directory_button, on_click=self._pick_template_dir
        )
        self._template_directory = layout.PathText(value=TEXTS.missing_template_directory)

        self._create_template_path = layout.PathText(is_file=True)
        self._overwrite_template = ft.Checkbox(
            label=TEXTS.get_file_exists(False), value=False, active_color="red"
        )
        self._create_template_btn = ft.FilledButton(
            TEXTS.create_template, on_click=self._create_template
        )

    def _create_result_controls(self):
        """Step 3: merge the template with CTD data into a result file"""
        self._metadata_surface_layer = layout.text_field(
            TEXTS.surface_layer, allowed=layout.DECIMAL
        )
        self._metadata_bottom_layer = layout.text_field(
            TEXTS.bottom_layer, allowed=layout.DECIMAL
        )
        self._metadata_max_depth_diff_allowed = layout.text_field(
            TEXTS.max_depth_diff_allowed, allowed=layout.DECIMAL
        )
        self._reset_depth_margins_btn = ft.Button(
            TEXTS.reset_depth_margins, on_click=self._reset_depth_margins
        )

        self._pick_template_file_btn = ft.Button(
            TEXTS.get_template_path_button, on_click=self._pick_template_file
        )
        self._use_template_path = layout.PathText(
            value=TEXTS.missing_use_template_path, is_file=True
        )
        self._open_template_file_btn = ft.Button(
            TEXTS.open_file_template, on_click=self._open_template_file
        )

        self._pick_ctd_dir_btn = ft.Button(
            TEXTS.get_ctd_directory_button, on_click=self._pick_ctd_dir
        )
        self._ctd_directory = layout.PathText(value=TEXTS.missing_ctd_directory)

        self._create_result_path = layout.PathText(is_file=True)
        self._overwrite_result = ft.Checkbox(
            label=TEXTS.get_file_exists(False), value=False, active_color="red"
        )
        self._open_result_file_btn = ft.Button(
            TEXTS.open_file_result, on_click=self._open_result_file
        )
        self._create_result_btn = ft.FilledButton(
            TEXTS.create_result, on_click=self._create_result
        )

    # ------------------------------------------------------------------
    # Layout: the whole page in one place. Move controls around here.
    # ------------------------------------------------------------------
    def _build_layout(self) -> list[ft.Control]:
        ph_from_crm_tab = ft.Container(
            padding=ft.Padding.only(top=style.TAB_CONTENT_TOP_PADDING),
            content=ft.Column(
                [
                    layout.title(TEXTS.title_title),
                    self._batch_nr,
                    layout.label_value(TEXTS.batch_alk_label, self._batch_alk),
                    layout.label_value(TEXTS.batch_dic_label, self._batch_dic),
                    layout.label_value(TEXTS.batch_salt_label, self._batch_salt),
                    ft.Row([self._batch_temp]),
                    layout.label_value(TEXTS.calculated_ph, self._batch_ph),
                    self._batch_measured_ph,
                    layout.label_value(TEXTS.deviation, self._batch_plot_value),
                ]
            ),
        )

        ph_from_tris_tab = ft.Container(
            padding=ft.Padding.only(top=style.TAB_CONTENT_TOP_PADDING),
            content=ft.Column(
                [
                    layout.title(TEXTS.tris_title),
                    self._tris_type,
                    ft.Row([self._tris_temp]),
                    layout.label_value(TEXTS.calculated_ph, self._tris_ph),
                    self._tris_measured_ph,
                    layout.label_value(TEXTS.deviation, self._tris_plot_value),
                ]
            ),
        )

        metadata_card = layout.card(
            bgcolor=COLORS.metadata,
            content=layout.field_column(
                layout.title(TEXTS.title_metadata),
                self._metadata_signature,
                self._metadata_project,
            ),
        )

        ph_card = layout.card(
            bgcolor=COLORS.batch,
            expand=style.PH_CARD_EXPAND,
            content=ft.Tabs(
                length=2,
                expand=True,
                content=ft.Column(
                    [
                        ft.TabBar(
                            scrollable=False,
                            tabs=[
                                ft.Tab(label=TEXTS.tab_tris),
                                ft.Tab(label=TEXTS.tab_crm),
                            ],
                        ),
                        ft.TabBarView(
                            expand=True,
                            controls=[ph_from_tris_tab, ph_from_crm_tab],
                        ),
                    ],
                    expand=True,
                ),
            ),
        )

        depth_card = layout.card(
            bgcolor=COLORS.metadata,
            expand=style.DEPTH_CARD_EXPAND,
            content=layout.field_column(
                layout.title_with_info(
                    TEXTS.title_ctd_matching,
                    TOOLTIP_TEXT.ctd,
                    style.INFO_DIALOG_CTD_CARD,
                ),
                self._metadata_surface_layer,
                self._metadata_bottom_layer,
                self._metadata_max_depth_diff_allowed,
                self._reset_depth_margins_btn,
            ),
        )

        correction_file_card = layout.card(
            bgcolor=COLORS.hydrofia_container,
            expand=1,
            content=ft.Column(
                [
                    layout.card_title(
                        TEXTS.title_create_excel,
                        TOOLTIP_TEXT.hydrofia_file,
                        style.INFO_DIALOG_UPPER_CARD,
                    ),
                    layout.path_row(
                        self._pick_hydrofia_file_btn,
                        self._hydrofia_file_path,
                    ),
                    layout.path_row(
                        self._pick_template_dir_btn,
                        self._template_directory,
                    ),
                    layout.labeled_row(
                        TEXTS.period_filter_label, self._year, self._month
                    ),
                    ft.Container(expand=True),
                    ft.Divider(),
                    layout.output_row(
                        self._create_template_btn,
                        TEXTS.create_file_label,
                        self._create_template_path,
                        self._overwrite_template,
                    ),
                ]
            ),
        )

        result_file_card = layout.card(
            bgcolor=COLORS.result_container,
            expand=1,
            content=ft.Column(
                [
                    layout.card_title(
                        TEXTS.title_merge_ctd_with_hydrofia,
                        TOOLTIP_TEXT.template_file,
                        style.INFO_DIALOG_LOWER_CARD,
                    ),
                    layout.path_row(
                        self._pick_template_file_btn,
                        self._use_template_path,
                        self._open_template_file_btn,
                    ),
                    layout.path_row(
                        self._pick_ctd_dir_btn,
                        self._ctd_directory,
                    ),
                    ft.Container(expand=True),
                    ft.Divider(),
                    layout.output_row(
                        self._create_result_btn,
                        TEXTS.create_file_label,
                        self._create_result_path,
                        self._overwrite_result,
                        self._open_result_file_btn,
                    ),
                ]
            ),
        )

        self._content = ft.Row(
            [
                ft.Column(
                    [metadata_card, ph_card, depth_card],
                    spacing=style.TOP_ROW_SPACING,
                    width=style.SIDE_COLUMN_WIDTH,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
                ft.Column(
                    [correction_file_card, result_file_card],
                    spacing=style.TOP_ROW_SPACING,
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
            ],
            spacing=style.TOP_ROW_SPACING,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            expand=True,
        )
        return [self._content]

    def _update_tris_ph(self, *args):
        """Show the pH and its deviation. Silent while the input is incomplete."""
        self._tris_ph.value = ""
        self._tris_plot_value.value = ""
        temp = layout.parse_float(self._tris_temp.value)
        if temp is not None:
            calculate_ph = TRIS_BUFFERS[self._tris_type.value]
            ph = round(float(calculate_ph(temp)), 3)
            self._tris_ph.value = str(ph)
            measured_ph = layout.parse_float(self._tris_measured_ph.value)
            if measured_ph is not None:
                self._tris_plot_value.value = str(round(ph - measured_ph, 4))
        self._tris_ph.update()
        self._tris_plot_value.update()

    def _update_batch_info(self, *args):
        try:
            batch = self._batches.get_batch(self._batch_nr.value)
        except InvalidBatchError as e:
            logger.warning(e)
            self._show_info(TEXTS.invalid_batch(self._batch_nr.value))
            batch = None
        self._batch_alk.value = str(batch.alk) if batch else ""
        self._batch_dic.value = str(batch.dic) if batch else ""
        self._batch_salt.value = str(batch.salinity) if batch else ""
        self.update_page()
        self._update_crm_ph()
        # self._batch_temp.focus()

    def _on_select_batch(self, *args):
        self._update_batch_info()
        saves.save()

    def _reset_depth_margins(self, *args):
        config = DEFAULT_DEPTH_MARGINS.copy()
        config.update(get_config())
        self._metadata_max_depth_diff_allowed.value = str(config["meta_diff"])
        self._metadata_max_depth_diff_allowed.update()
        self._metadata_surface_layer.value = str(config["meta_surface"])
        self._metadata_surface_layer.update()
        self._metadata_bottom_layer.value = str(config["meta_bottom"])
        self._metadata_bottom_layer.update()

    def _crm_inputs(self) -> tuple[str, str, str]:
        return (
            self._batch_nr.value,
            self._batch_temp.value,
            self._batch_measured_ph.value,
        )

    def _update_crm_ph(self, *args):
        """Show the pH and its deviation. Silent while the input is incomplete."""
        inputs = self._crm_inputs()
        batch_nr, temp_text, measured_text = inputs
        ph_text = ""
        plot_text = ""
        temp = layout.parse_float(temp_text)
        batch = None
        if temp is not None:
            # An invalid batch is reported by _update_batch_info
            with contextlib.suppress(InvalidBatchError):
                batch = self._batches.get_batch(batch_nr)
        if batch:
            ph = round(float(batch.get_ph(temperature=temp)), 3)
            ph_text = str(ph)
            measured_ph = layout.parse_float(measured_text)
            if measured_ph is not None:
                plot_text = str(round(ph - measured_ph, 4))
        # The calculation is slow enough for a newer edit to arrive, which then takes over
        if self._crm_inputs() != inputs:
            return
        self._batch_ph.value = ph_text
        self._batch_plot_value.value = plot_text
        self._batch_ph.update()
        self._batch_plot_value.update()

    def _on_pick_hydrofia_file_path(self, files: list[ft.FilePickerFile]):
        self._close_banner()
        if not files:
            return
        path = files[0].path
        self._set_hydrofia_file_path(path)

    def _set_hydrofia_file_path(self, text=None):
        if not text:
            return
        self._hydrofia_file_path.value = text
        self._update_period_options()
        self._update_create_template_path()
        self.update_page()

    def _update_period_options(self):
        """Offer only the years with samples in the HydroFIA file, latest selected.

        A file that is not a HydroFIA export is reported and deselected.
        """
        path = self.hydrofia_file_path
        try:
            self._periods = (
                hydrofia.get_periods_in_hydrofia_export_file(path) if path else {}
            )
        except InvalidHydrofiaFileError as e:
            logger.warning(e)
            self._show_info(TEXTS.invalid_hydrofia_file(path.name))
            self.hydrofia_file_path = None
            self._periods = {}
        self._year.options = [ft.DropdownOption(str(y)) for y in self._periods]
        self._year.value = str(max(self._periods)) if self._periods else None
        self._year.update()
        self._month.value = self._month_all_option
        self._update_month_options()

    def _update_month_options(self):
        """Offer only the months with samples in the selected year."""
        months = self._periods.get(int(self._year.value), []) if self._year.value else []
        options = [self._month_all_option, *map(str, months)]
        self._month.options = [ft.DropdownOption(option) for option in options]
        if self._month.value not in options:
            self._month.value = self._month_all_option
        self._month.update()

    def _on_select_year(self, *args):
        self._update_month_options()
        self._update_create_template_path()

    def _on_pick_ctd_dir(self, path: str | None):
        self._close_banner()
        if not path:
            return
        self.ctd_directory = path
        saves.save()

    def _on_pick_template_dir(self, path: str | None):
        """Related to the creation of the TEMPLATE"""
        self._close_banner()
        if not path:
            return
        self.template_directory = path
        self._update_create_template_path()

    def _on_pick_template_file(self, files: list[ft.FilePickerFile]):
        """Related to creation of RESULT file"""
        self._close_banner()
        logger.info(f"{files=}")
        if not files:
            return
        self.use_template_path = files[0].path
        self._update_create_result_path()

    # def _set_default_result_file_name(self):
    #     """Sets default name if no name is given"""
    #     if self.result_file_name:
    #         return
    #     if not self.use_template_path:
    #         return
    #     name = self.use_template_path.stem + '_result'
    #     self.result_file_name = name
    #     self.create_result_path = None

    def _check_create_template_path_exists(self, *args):
        if self.create_template_path and self.create_template_path.exists():
            disabled = False
            overwrite = False
            label = TEXTS.get_file_exists(True)
        else:
            disabled = True
            overwrite = True
            label = TEXTS.get_file_exists(False)
        logger.info(f"TEMPLATE: {disabled=}")
        logger.info(f"{label=}")

        self._overwrite_template.disabled = disabled
        self._overwrite_template.visible = not disabled
        self._overwrite_template.label = label
        self._overwrite_template.value = overwrite
        self._overwrite_template.update()

    def _check_create_result_path_exists(self):
        path = self.create_result_path
        if path and path.exists():
            disabled = False
            overwrite = False
            label = TEXTS.get_file_exists(True)
            self._open_result_file_btn.visible = True
            self._open_result_file_btn.update()
        else:
            disabled = True
            overwrite = True
            label = TEXTS.get_file_exists(False)
            self._open_result_file_btn.visible = False
            self._open_result_file_btn.update()
        logger.info(f"{disabled=}")
        logger.info(f"{label=}")

        self._overwrite_result.disabled = disabled
        self._overwrite_result.visible = not disabled
        self._overwrite_result.label = label
        self._overwrite_result.value = overwrite
        self._overwrite_result.update()

    def _open_template_directory(self, *args):
        if (
            not self.template_directory
            or self.template_directory == TEXTS.missing_template_directory
        ):
            return
        utils.open_file_in_default_program(self.template_directory)

    def _open_template_file(self, *args):
        if not self.use_template_path or not self.use_template_path.exists():
            return
        utils.open_file_in_default_program(self.use_template_path)

    def _open_result_file(self, *args):
        if not self.create_result_path or not self.create_result_path.exists():
            return
        utils.open_file_in_default_program(self.create_result_path)

    def _create_template(self, *args):
        if not self._create_template_ok():
            return
        try:
            year = int(self._year.value)
            month = (
                int(self._month.value)
                if self._month.value != self._month_all_option
                else None
            )
            self._disable_toggle_buttons()
            self._show_info(TEXTS.info_creating_template, status="working")
            path = hydrofia.create_template(
                template_path=self.create_template_path,
                hydrofia_export_path=self._hydrofia_file_path.value,
                overwrite=self._overwrite_template.value,
                year=year,
                month=month,
            )
            self._check_create_template_path_exists()
            self._show_info(TEXTS.info_creating_template_done(path), status="good")
            self.use_template_path = str(path)
            self.template_directory = self.template_directory
            self._update_create_result_path()
            saves.save()
        except Exception as e:
            logger.error(e)
            self._show_info(f"Något gick fel:\n{e}")
            raise
        finally:
            self._enable_toggle_buttons()

    def _create_result(self, *args):
        if not self._create_result_ok():
            return
        try:
            self._disable_toggle_buttons()
            self._show_info(TEXTS.info_creating_result, status="working")
            calc_object = hydrofia.get_calculated_object(
                template_path=self.use_template_path,
                ctd_directory=self.ctd_directory,
                signature=self.metadata_signature,
                project=self.metadata_project,
                max_depth_diff_allowed=self.metadata_max_depth_diff_allowed,
                surface_layer_depth=self.metadata_surface_layer,
                bottom_layer_depth=self.metadata_bottom_layer,
            )

            hydrofia.create_xlsx_result_file_from_calc_object(
                calc_object=calc_object,
                path=self.create_result_path,
                overwrite=self._overwrite_result.value,
                project=self._metadata_project.value.strip(),
                signature=self._metadata_signature.value.strip(),
            )

            hydrofia.create_txt_archive_file_from_calc_object(
                calc_object=calc_object,
                path=self.create_result_path.with_suffix(".txt"),
                overwrite=self._overwrite_result.value,
            )
            # hydrofia.create_xlsx_result_file(
            #   template_path=self.use_template_path,
            #   ctd_directory=self.ctd_directory,
            #   result_file_path=self.create_result_path,
            #   signature=self.metadata_signature,
            #   project=self.metadata_project,
            #   max_depth_diff_allowed=self.metadata_max_depth_diff_allowed,
            #   surface_layer_depth=self.metadata_surface_layer,
            #   bottom_layer_depth=self.metadata_bottom_layer,
            #   overwrite=self._overwrite_result.value)
            # self._check_create_template_path_exists()
            self._show_info(
                TEXTS.get_info_creating_result_done(self.create_result_path),
                status="good",
            )
            self._check_create_result_path_exists()
            self._update_create_result_path()
            saves.save()
        except Exception as e:
            logger.error(e)
            self._show_info(f"Något gick fel:\n{e}")
            raise
        finally:
            self._enable_toggle_buttons()

    def _create_template_ok(self):
        if not self.create_template_path:
            self._show_info(TEXTS.missing_template_path)
            return False
        if not self.hydrofia_file_path:
            self._show_info(TEXTS.missing_hydrofia_file_path)
            return False
        if not self.hydrofia_file_path.exists():
            self._show_info(TEXTS.non_existing_hydrofia_path)
            return False
        if self.create_template_path.exists() and not self._overwrite_template.value:
            self._show_info(TEXTS.select_overwrite(self.create_template_path))
            return False
        return True

    def _create_result_ok(self) -> bool:
        error = None
        if not self.use_template_path:
            error = TEXTS.missing_use_template_path
        elif not self.use_template_path.exists():
            error = TEXTS.non_existing_template_path
        elif not self.ctd_directory:
            error = TEXTS.missing_ctd_directory
        elif not self.ctd_directory.exists():
            error = TEXTS.non_existing_ctd_path
        elif not self.create_result_path:
            error = TEXTS.missing_result_path
        elif self.create_result_path.exists() and not self._overwrite_result.value:
            error = TEXTS.select_overwrite(self.create_result_path)
        elif not self._metadata_project.value.strip():
            error = TEXTS.missing_metadata("projekt")
        elif not self._metadata_signature.value.strip():
            error = TEXTS.missing_metadata("signatur")

        if error:
            self._show_info(error)
            return False

        return True

    @staticmethod
    def filter_path(path):
        # return str.split('.')[0]
        # return str.strip(',.-\!"#¤%&/()=')
        return re.sub(r"[^A-Za-z0-9åäö_\-]+", "", path)

    # def _on_change_template_export_file_name(self, *args):
    #     name = self.filter_path(self.template_export_file_name)
    #     self.template_export_file_name = name
    #     self._update_create_template_path()

    # def _on_blur_template_export_file_name(self, *args):
    #     name = self.filter_path(self.template_export_file_name)
    #     if not name:
    #         name = hydrofia.get_default_template_path().stem
    #     self.template_export_file_name = name
    #     self._update_create_template_path()

    def _update_create_template_path(self, *args):
        """Updates the template path related to the creation of template"""
        path = ""
        if self.template_directory and self.hydrofia_file_path and self._year.value:
            proj = self._metadata_project.value.strip()
            if not proj:
                self.create_template_path = None
                return
            year = int(self._year.value)
            month = self._month.value
            month = None if month == "ALLA" else int(month)
            id_string = hydrofia.get_id_string_for_hydrofia_export_file(
                self.hydrofia_file_path, year=year, month=month
            )
            if not id_string:
                self.create_template_path = None
                return
            name = f"{proj}_{id_string}{TEMPLATE_STEM_ENDING}.xlsx"
            path = pathlib.Path(self.template_directory, name)
        self.create_template_path = path
        # self._check_create_template_path_exists()

    # def _on_change_result_file_name(self, *args):
    #     name = self.filter_path(self.result_file_name)
    #     self.result_file_name = name
    #     self._update_create_result_path()

    # def _on_blur_result_file_name(self, *args):
    #     name = self.filter_path(self.result_file_name)
    #     if not name:
    #         if self.use_template_path:
    #             name = self.use_template_path.stem + '_result'
    #         else:
    #             name = ''
    #     self.result_file_name = name
    #     self._update_create_result_path()

    def _update_create_result_path(self):
        """Updates the template path related to the creation of template"""
        template_path = self.use_template_path
        if not template_path:
            self.create_result_path = None
            self._check_create_result_path_exists()
            return
        directory = template_path.parent
        stem = template_path.stem
        stem = stem.removesuffix(TEMPLATE_STEM_ENDING)
        stem = stem + RESULT_STEM_ENDING
        path = pathlib.Path(directory, stem + ".xlsx")
        self.create_result_path = path
        self._check_create_result_path_exists()

    @property
    def hydrofia_file_path(self) -> pathlib.Path | None:
        value = self._hydrofia_file_path.value
        if not value or value == TEXTS.missing_hydrofia_file_path:
            return None
        return pathlib.Path(value)

    @hydrofia_file_path.setter
    def hydrofia_file_path(self, path=None):
        if not path:
            path = TEXTS.missing_hydrofia_file_path
        self._hydrofia_file_path.value = str(path)
        self._hydrofia_file_path.update()

    @property
    def template_directory(self) -> pathlib.Path | None:
        value = self._template_directory.value
        if not value or value == TEXTS.missing_template_directory:
            return None
        return pathlib.Path(value)

    @template_directory.setter
    def template_directory(self, path=None):
        # self._open_template_dir_btn.visible = True
        if not path:
            path = TEXTS.missing_template_directory
            # self._open_template_dir_btn.visible = False
        # self._open_template_dir_btn.update()
        self._template_directory.value = str(path)
        self._template_directory.update()

    @property
    def create_template_path(self) -> pathlib.Path | None:
        value = self._create_template_path.value
        if not value or value == TEXTS.missing_template_path:
            return None
        return pathlib.Path(value)

    @create_template_path.setter
    def create_template_path(self, path=None):
        if not path:
            path = TEXTS.missing_template_path
            # if self.template_export_file_name and self.template_directory:
            #     path = pathlib.Path(
            #       self.template_directory, self.template_export_file_name + '.xlsx'
            #     )
        self._create_template_path.value = str(path)
        self._create_template_path.update()
        self._check_create_template_path_exists()

    # @property
    # def template_export_file_name(self) -> str:
    #     return self._template_export_file_name.value
    #
    # @template_export_file_name.setter
    # def template_export_file_name(self, name=None):
    #     self._template_export_file_name.value = name
    #     self._template_export_file_name.update()

    @property
    def use_template_path(self) -> pathlib.Path | None:
        value = self._use_template_path.value
        if not value or value == TEXTS.missing_use_template_path:
            return None
        return pathlib.Path(value)

    @use_template_path.setter
    def use_template_path(self, path=None):
        self._open_template_file_btn.visible = True
        if not path:
            path = TEXTS.missing_use_template_path
            self._open_template_file_btn.visible = False
        self._open_template_file_btn.update()
        self._use_template_path.value = str(path)
        self._use_template_path.update()

    def _check_use_template_path(self):
        value = self._use_template_path.value
        visible = False
        if value and pathlib.Path(value).exists():
            visible = True
        self._open_template_file_btn.visible = visible
        self._open_template_file_btn.update()

    @property
    def create_result_path(self) -> pathlib.Path | None:
        value = self._create_result_path.value
        if not value or value == TEXTS.missing_result_path:
            return None
        return pathlib.Path(value)

    @create_result_path.setter
    def create_result_path(self, path=None):
        if not path:
            path = TEXTS.missing_result_path
        self._create_result_path.value = str(path)
        self._create_result_path.update()

    # @property
    # def result_file_name(self) -> str:
    #     return self._result_file_name.value
    #
    # @result_file_name.setter
    # def result_file_name(self, path=None):
    #     self._result_file_name.value = path
    #     self._result_file_name.update()

    @property
    def ctd_directory(self) -> pathlib.Path | None:
        value = self._ctd_directory.value
        if not value or value == TEXTS.missing_ctd_directory:
            return None
        return pathlib.Path(value)

    @ctd_directory.setter
    def ctd_directory(self, path=None):
        if not path:
            path = TEXTS.missing_ctd_directory
        self._ctd_directory.value = path
        self._ctd_directory.update()

    @property
    def metadata_signature(self) -> str:
        return self._metadata_signature.value

    @property
    def metadata_project(self) -> str:
        return self._metadata_project.value

    @property
    def metadata_surface_layer(self) -> float | None:
        value = self._metadata_surface_layer.value
        try:
            return float(value.strip())
        except ValueError:
            return None

    @property
    def metadata_bottom_layer(self) -> float | None:
        value = self._metadata_bottom_layer.value
        try:
            return float(value.strip())
        except ValueError:
            return None

    @property
    def metadata_max_depth_diff_allowed(self) -> float | None:
        value = self._metadata_max_depth_diff_allowed.value
        try:
            return float(value.strip())
        except ValueError:
            return None


def main(log_in_console):
    return FletApp(log_in_console=log_in_console)


def run() -> None:
    """Entry point for the console script."""
    main(log_in_console="INFO")
