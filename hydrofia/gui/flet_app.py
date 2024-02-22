import datetime
import logging.handlers
import pathlib
import re
import sys

import hydrofia
from hydrofia.gui.tooltip_texts import TooltipTexts, get_tooltip_widget
from hydrofia.gui.texts import Texts
from hydrofia.gui.colors import Colors
from hydrofia.gui import saves
from hydrofia import utils

import flet as ft
from flet_core.constrained_control import ConstrainedControl

logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False):
    DIRECTORY = pathlib.Path(sys.executable).parent
else:
    DIRECTORY = pathlib.Path(__file__).parent

TOOLTIP_TEXT = TooltipTexts()

TEXTS = Texts()
COLORS = Colors()


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

        self._month_all_option = 'ALLA'

        self._toggle_buttons: list[ConstrainedControl] = []

        self.logging_level = 'DEBUG'
        self.logging_format = '%(asctime)s [%(levelname)10s]    %(pathname)s [%(lineno)d] => %(funcName)s():    %(message)s'
        self.logging_format_stdout = '[%(levelname)10s] %(filename)s: %(funcName)s() [%(lineno)d] %(message)s'
        self._setup_logger()

        self.app = ft.app(target=self.main)

    @property
    def _log_directory(self):
        path = pathlib.Path(pathlib.Path.home(), 'logs')
        path.mkdir(parents=True, exist_ok=True)
        return path

    def main(self, page: ft.Page):
        self.page = page
        self.page.title = TEXTS.title
        self.page.window_height = 1100
        self.page.window_width = 1600
        self._initiate_pickers()
        self._build()
        self._initiate_banner()

        saves.add_control('_hydrofia_file_path', self._hydrofia_file_path)
        saves.add_control('_template_directory', self._template_directory)
        saves.add_control('_use_template_path', self._use_template_path)
        saves.add_control('_ctd_directory', self._ctd_directory)
        saves.add_control('_metadata_signature', self._metadata_signature)
        saves.add_control('_metadata_project', self._metadata_project)
        saves.add_control('_metadata_surface_layer', self._metadata_surface_layer)
        saves.add_control('_metadata_bottom_layer', self._metadata_bottom_layer)
        saves.add_control('_metadata_max_depth_diff_allowed', self._metadata_max_depth_diff_allowed)

        saves.load(self)

        self._on_blur_template_export_file_name()
        self._on_blur_result_file_name()

        # self.use_template_path = self.use_template_path
        # self.template_directory = self.template_directory
        # self.create_result_path = self.create_result_path

    def update_page(self):
        self.page.update()

    def _setup_logger(self, **kwargs):
        name = 'hydrofia'
        # self.logger = logging.getLogger(name)
        self.logger = logging.getLogger()
        self.logger.setLevel(self.logging_level)

        debug_file_path = pathlib.Path(self._log_directory, f'{name}_debug.log')
        handler = logging.handlers.TimedRotatingFileHandler(str(debug_file_path), when='H', interval=3, backupCount=10)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(self.logging_format)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        debug_file_path = pathlib.Path(self._log_directory, f'{name}_warning.log')
        handler = logging.handlers.TimedRotatingFileHandler(str(debug_file_path), when='D', interval=1, backupCount=14)
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
        self._hydrofia_file_picker = ft.FilePicker(on_result=self._on_pick_hydrofia_file_path)
        # Setting properties not working. Report bug!
        # self._hydrofia_file_picker.dialog_title = TEXTS.dialog_title_hydrofia_file_path
        # self._hydrofia_file_picker.initial_directory
        # self._hydrofia_file_picker.file_type
        # self._hydrofia_file_picker.allowed_extensions = ['txt']
        # self._hydrofia_file_picker.allow_multiple = False

        self._template_directory_picker = ft.FilePicker(on_result=self._on_pick_template_dir)
        # self._template_directory_picker.dialog_title = TEXTS.dialog_title_template_directory
        # self._template_directory_picker.initial_directory

        self._ctd_directory_picker = ft.FilePicker(on_result=self._on_pick_ctd_dir)
        # self._template_directory_picker.dialog_title = TEXTS.dialog_title_template_directory
        # self._template_directory_picker.initial_directory

        self._template_file_picker = ft.FilePicker(on_result=self._on_pick_template_file)
        # Setting properties not working. Report bug!
        # self._template_file_picker.dialog_title = TEXTS.dialog_title_template_file
        # self._template_file_picker.initial_directory
        # self._template_file_picker.file_type
        # self._template_file_picker.allowed_extensions = ['txt']
        # self._template_file_picker.allow_multiple = False

        self.page.overlay.append(self._hydrofia_file_picker)
        self.page.overlay.append(self._template_directory_picker)
        self.page.overlay.append(self._ctd_directory_picker)
        self.page.overlay.append(self._template_file_picker)

    def _initiate_banner(self):
        self.banner_content = ft.Column()

        self.page.banner = ft.Banner(
            # bgcolor=ft.colors.AMBER_100,
            # bgcolor=COLORS.banner(),
            leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.AMBER, size=40),
            content=self.banner_content,
            force_actions_below=True,
            actions=[
                ft.TextButton("OK!", on_click=self._close_banner),
            ],
        )

    def _set_banner(self, color):
        self.banner_content = ft.Column()

        self.page.banner = ft.Banner(
            # bgcolor=ft.colors.AMBER_100,
            bgcolor=color,
            leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.AMBER, size=40),
            content=self.banner_content,
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
        if not self.page.banner.open:
            return
        self.page.banner.open = False
        self.page.update()

    # def _show_banner(self, e=None):
    def _show_banner(self):
        self.page.banner.open = True
        self.page.update()

    def _show_info(self, text, status='bad'):
        self._set_banner(COLORS.banner(status))
        self.banner_content.controls = [ft.Text(text)]
        # self.page.banner.bgcolor = COLORS.banner(status)
        self._show_banner()

    def _build(self):
        col = ft.Column(
            spacing=10,
            expand=True,
            #scroll=ft.ScrollMode.AUTO
        )

        self.page.controls.append(self._get_hydrofia_container())
        self.page.controls.append(self._get_template_container())

        # container = ft.Container(content=col,
        #                          # bgcolor=COLORS.hydrofia_file_path,
        #                          border_radius=10,
        #                          padding=10,
        #                          expand=True)
        #
        # self.page.controls.append(container)

        # self.page.controls.append(self._get_hydrofia_container())
        # self.page.controls.append(self._get_template_container())

        self._open_template_dir_btn.visible = False
        self._open_template_file_btn.visible = False
        self._open_result_file_btn.visible = False

        self.update_page()

    def _get_hydrofia_container(self):

        export_row = ft.Row(
            # alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=20
        )

        btn = ft.ElevatedButton(TEXTS.get_hydrofia_export_button, on_click=lambda _:
                                self._hydrofia_file_picker.pick_files(
                                    dialog_title=TEXTS.dialog_title_hydrofia_file_path,
                                    allowed_extensions=['txt'],
                                    allow_multiple=False
                                ))

        self._hydrofia_file_path = ft.Text(TEXTS.missing_hydrofia_file_path)

        # Filter on year
        year_options = []
        for y in range(2022, datetime.datetime.now().year+1):
            year_options.append(ft.dropdown.Option(str(y)))
        self._year = ft.Dropdown(
            label='År',
            hint_text='Filtrera på år',
            options=year_options,
            dense=True
        )
        self._year.value = str(datetime.datetime.now().year)

        # Filter on month
        month_options = [ft.dropdown.Option(self._month_all_option)]
        for m in range(1, 13):
            month_options.append(ft.dropdown.Option(str(m)))
        self._month = ft.Dropdown(
            label='Månad',
            hint_text='Filtrera på månad',
            options=month_options,
            autofocus=True,
            dense=True,
        )
        self._month.value = self._month_all_option

        dir_btn = ft.ElevatedButton(TEXTS.get_template_directory_button, on_click=lambda _:
        self._template_directory_picker.get_directory_path(
            dialog_title=TEXTS.dialog_title_template_directory
        ))

        self._open_template_dir_btn = ft.ElevatedButton(TEXTS.open_directory, on_click=self._open_template_directory)

        self._template_directory = ft.Text(TEXTS.missing_template_directory)
        # self.template_directory = str(hydrofia.get_default_template_path().parent)

        create_path_label = ft.Text(TEXTS.create_file_label)
        self._create_template_path = ft.Text()

        self._overwrite_template = ft.Switch(label=TEXTS.overwrite, value=False, active_color='red')

        self._toggle_buttons.append(btn)
        self._toggle_buttons.append(dir_btn)
        self._toggle_buttons.append(self._open_template_dir_btn)
        self._toggle_buttons.append(self._overwrite_template)

        path_row = ft.Row()
        filter_row = ft.Row()
        folder_row = ft.Row()
        create_path_row = ft.Row()

        path_row.controls.append(btn)
        path_row.controls.append(self._hydrofia_file_path)

        filter_row.controls.append(self._year)
        filter_row.controls.append(self._month)

        folder_row.controls.append(dir_btn)
        folder_row.controls.append(self._template_directory)
        folder_row.controls.append(self._open_template_dir_btn)

        create_path_row.controls.append(create_path_label)
        create_path_row.controls.append(self._create_template_path)

        overwrite_row = ft.Row()
        overwrite_row.controls.append(self._overwrite_template)

        col = ft.Column()
        col.controls.append(path_row)
        col.controls.append(filter_row)
        col.controls.append(folder_row)
        col.controls.append(create_path_row)
        col.controls.append(overwrite_row)

        tt = get_tooltip_widget(TOOLTIP_TEXT.hydrofia_file)
        tt.content = col

        export_row.controls.append(tt)
        export_row.controls.append(self._get_create_template_container())

        main_column = ft.Column()
        main_column.controls.append(ft.Text(TEXTS.title_create_excel,
                                            size=30,
                                            weight=ft.FontWeight.W_400))
        main_column.controls.append(export_row)

        #container = ft.Container(content=export_row,
        container = ft.Container(content=main_column,
                                 bgcolor=COLORS.hydrofia_file_path,
                                 border_radius=10,
                                 padding=10,
                                 expand=1)

        return container

    def _get_template_container(self):

        template_col = ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=2)

        file_btn = ft.ElevatedButton(TEXTS.get_template_path_button, on_click=lambda _:
                                    self._template_file_picker.pick_files(
                                        dialog_title=TEXTS.dialog_title_template_file,
                                        allowed_extensions=['xlsx'],
                                        allow_multiple=False
                                    ))

        self._use_template_path = ft.Text(TEXTS.missing_template_path)

        self._open_template_file_btn = ft.ElevatedButton(TEXTS.open_file, on_click=self._open_template_file)

        dir_btn = ft.ElevatedButton(TEXTS.get_ctd_directory_button, on_click=lambda _:
        self._ctd_directory_picker.get_directory_path(
            dialog_title=TEXTS.dialog_title_ctd_directory
        ))

        self._ctd_directory = ft.Text(TEXTS.missing_ctd_directory)

        create_path_label = ft.Text(TEXTS.create_file_label)
        self._create_result_path = ft.Text()

        self._overwrite_result = ft.Switch(label=TEXTS.overwrite, value=False, active_color='red')

        self._open_result_file_btn = ft.ElevatedButton(TEXTS.open_file, on_click=self._open_result_file)

        self._toggle_buttons.append(self._open_template_file_btn)
        self._toggle_buttons.append(self._open_result_file_btn)
        self._toggle_buttons.append(file_btn)
        self._toggle_buttons.append(dir_btn)

        file_row = ft.Row()
        ctd_row = ft.Row()
        create_path_row = ft.Row()

        file_row.controls.append(file_btn)
        file_row.controls.append(self._use_template_path)
        file_row.controls.append(self._open_template_file_btn)

        ctd_row.controls.append(dir_btn)
        ctd_row.controls.append(self._ctd_directory)

        create_path_row.controls.append(create_path_label)
        create_path_row.controls.append(self._create_result_path)

        overwrite_row = ft.Row()
        overwrite_row.controls.append(self._overwrite_result)
        overwrite_row.controls.append(self._open_result_file_btn)

        col = ft.Column()
        col.controls.append(file_row)
        col.controls.append(ctd_row)
        col.controls.append(create_path_row)
        col.controls.append(overwrite_row)

        tt = get_tooltip_widget(TOOLTIP_TEXT.template_file)
        tt.expand = 1
        tt.content = col

        template_col.controls.append(tt)

        template_lower_row = ft.Row(
            #alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10,
            expand=2
        )

        template_lower_row.controls.append(self._get_metadata_container())
        template_lower_row.controls.append(self._get_create_result_container())

        template_col.controls.append(template_lower_row)

        main_column = ft.Column()
        main_column.controls.append(ft.Text(TEXTS.title_merge_ctd_with_hydrofia,
                                            size=30,
                                            weight=ft.FontWeight.W_400))
        main_column.controls.append(template_col)

        #container = ft.Container(content=template_col,
        container = ft.Container(content=main_column,
                                 bgcolor=COLORS.template_path,
                                 border_radius=10,
                                 padding=10,
                                 expand=2)

        return container

    def _get_create_template_container(self):

        export_row = ft.Row(
            expand=True
        )

        self._template_export_file_name = ft.TextField(label=TEXTS.template_export_file_name,
                                                       dense=True,
                                                       on_change=self._on_change_template_export_file_name,
                                                       on_blur=self._on_blur_template_export_file_name)

        btn = ft.ElevatedButton(TEXTS.create_template, on_click=self._create_template)
        self._toggle_buttons.append(btn)

        col = ft.Column()
        col.controls.append(self._template_export_file_name)
        col.controls.append(btn)

        tt = get_tooltip_widget(TOOLTIP_TEXT.create_template)
        tt.content = col

        export_row.controls.append(tt)

        container = ft.Container(content=export_row,
                                 bgcolor=COLORS.export_template,
                                 border_radius=10,
                                 padding=30,
                                 expand=True)

        return container

    def _get_create_result_container(self):

        export_row = ft.Row(
            expand=True
        )

        self._result_file_name = ft.TextField(label=TEXTS.result_file_name,
                                              dense=True,
                                              on_change=self._on_change_result_file_name,
                                              on_blur=self._on_blur_result_file_name
                                              )

        btn = ft.ElevatedButton(TEXTS.create_result, on_click=self._create_result)
        self._toggle_buttons.append(btn)

        col = ft.Column(
            #expand=True
        )
        col.controls.append(self._result_file_name)
        col.controls.append(btn)

        tt = get_tooltip_widget(TOOLTIP_TEXT.create_result)
        tt.content = col

        export_row.controls.append(tt)

        container = ft.Container(content=export_row,
                                 bgcolor=COLORS.export_result,
                                 border_radius=10,
                                 padding=10,
                                 # expand=True
                                 )

        return container

    def _get_metadata_container(self):

        export_row = ft.Row(
            # scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        dence = True

        self._metadata_signature = ft.TextField(label=TEXTS.signature,
                                                dense=dence,
                                                )

        self._metadata_project = ft.TextField(label=TEXTS.project,
                                              dense=dence,
                                              )

        self._metadata_surface_layer = ft.TextField(label=TEXTS.surface_layer,
                                              dense=dence,
                                              )

        self._metadata_bottom_layer = ft.TextField(label=TEXTS.bottom_layer,
                                                    dense=dence,
                                                    )

        self._metadata_max_depth_diff_allowed = ft.TextField(label=TEXTS.max_depth_diff_allowed,
                                              dense=dence,
                                              )

        row = ft.Row()
        col1 = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
            # expand=True,
            spacing=20
        )

        col2 = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
            # expand=True,
            spacing=20
        )
        row.controls.append(col1)
        row.controls.append(col2)
        col1.controls.append(self._metadata_signature)
        col1.controls.append(self._metadata_project)
        col1.controls.append(self._metadata_surface_layer)
        col2.controls.append(self._metadata_bottom_layer)
        col2.controls.append(self._metadata_max_depth_diff_allowed)

        tt = get_tooltip_widget(TOOLTIP_TEXT.metadata)
        tt.content = row

        export_row.controls.append(tt)

        container = ft.Container(content=export_row,
                                 bgcolor=COLORS.metadata,
                                 border_radius=10,
                                 padding=10,
                                 expand=True
                                 )

        return container

    def _on_pick_hydrofia_file_path(self, e: ft.FilePickerResultEvent):
        self._close_banner()
        if not e.files:
            return
        path = e.files[0].path
        self._set_hydrofia_file_path(path)

    def _set_hydrofia_file_path(self, text=None):
        if not text:
            return
        # TODO: Validate file
        self._hydrofia_file_path.value = text
        self.update_page()

    def _on_pick_ctd_dir(self, e: ft.FilePickerResultEvent):
        self._close_banner()
        if not e.path:
            return
        self.ctd_directory = e.path

    def _on_pick_template_dir(self, e: ft.FilePickerResultEvent):
        """Related to the creation of the TEMPLATE"""
        self._close_banner()
        if not e.path:
            return
        self.template_directory = e.path
        self._update_create_template_path()

    def _on_pick_template_file(self, e: ft.FilePickerResultEvent):
        """Related to creation of RESULT file"""
        self._close_banner()
        logger.info(f'{e.files=}')
        if not e.files:
            return
        self.use_template_path = e.files[0].path
        self._set_default_result_file_name()
        self._update_create_result_path()

    def _set_default_result_file_name(self):
        """Sets default name if no name is given"""
        if self.result_file_name:
            return
        if not self.use_template_path:
            return
        name = self.use_template_path.stem + '_result'
        self.result_file_name = name
        self.create_result_path = None

    def _check_create_template_path_exists(self):
        if self.create_template_path and self.create_template_path.exists():
            disabled = False
            label = TEXTS.get_file_exists(True)
        else:
            disabled = True
            label = TEXTS.get_file_exists(False)
        logger.info(f'{disabled=}')
        logger.info(f'{label=}')

        self._overwrite_template.disabled = disabled
        self._overwrite_template.label = label
        self._overwrite_template.update()

    def _check_create_result_path_exists(self):
        if self.create_result_path and self.create_result_path.exists():
            disabled = False
            label = TEXTS.get_file_exists(True)
            self._open_result_file_btn.visible = True
            self._open_result_file_btn.update()
        else:
            disabled = True
            label = TEXTS.get_file_exists(False)
            self._open_result_file_btn.visible = False
            self._open_result_file_btn.update()
        logger.info(f'{disabled=}')
        logger.info(f'{label=}')

        self._overwrite_result.disabled = disabled
        self._overwrite_result.label = label
        self._overwrite_result.update()

    def _open_template_directory(self, *args):
        if not self.template_directory or self.template_directory == TEXTS.missing_template_directory:
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
            month = int(self._month.value) if self._month.value != self._month_all_option else None
            self._disable_toggle_buttons()
            self._show_info(TEXTS.info_creating_template, status='working')
            path = hydrofia.create_template(template_path=self.create_template_path,
                                            hydrofia_export_path=self._hydrofia_file_path.value,
                                            overwrite=self._overwrite_template.value,
                                            year=year,
                                            month=month)
            self._check_create_template_path_exists()
            self._show_info(TEXTS.info_creating_template_done(path), status='good')
            self.use_template_path = str(path)
            self._set_default_result_file_name()
            self.template_directory = self.template_directory
            saves.save()
        except Exception as e:
            logger.error(e)
            self._show_info(f'Något gick fel:\n{e}')
            raise
        finally:
            self._enable_toggle_buttons()

    def _create_result(self, *args):
        if not self._create_result_ok():
            return
        try:
            self._disable_toggle_buttons()
            self._show_info(TEXTS.info_creating_result, status='working')
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
                overwrite=self._overwrite_result.value
            )

            hydrofia.create_txt_archive_file_from_calc_object(
                calc_object=calc_object,
                path=self.create_result_path.with_suffix('.txt'),
                overwrite=self._overwrite_result.value
            )
            # hydrofia.create_xlsx_result_file(template_path=self.use_template_path,
            #                                           ctd_directory=self.ctd_directory,
            #                                           result_file_path=self.create_result_path,
            #                                           signature=self.metadata_signature,
            #                                           project=self.metadata_project,
            #                                           max_depth_diff_allowed=self.metadata_max_depth_diff_allowed,
            #                                           surface_layer_depth=self.metadata_surface_layer,
            #                                           bottom_layer_depth=self.metadata_bottom_layer,
            #                                           overwrite=self._overwrite_result.value)
            # self._check_create_template_path_exists()
            self._show_info(TEXTS.get_info_creating_result_done(self.create_result_path), status='good')
            self._check_create_result_path_exists()
            self._update_create_result_path()
            saves.save()
        except Exception as e:
            logger.error(e)
            self._show_info(f'Något gick fel:\n{e}')
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

    def _create_result_ok(self):
        if not self.use_template_path:
            self._show_info(TEXTS.missing_template_path)
            return False
        if not self.use_template_path.exists():
            self._show_info(TEXTS.non_existing_template_path)
        if not self.ctd_directory:
            self._show_info(TEXTS.missing_ctd_directory)
            return False
        if not self.ctd_directory.exists():
            self._show_info(TEXTS.non_existing_ctd_path)
            return False
        if not self.create_result_path:
            self._show_info(TEXTS.missing_result_path)
            return False
        if self.create_result_path.exists() and not self._overwrite_result.value:
            self._show_info(TEXTS.select_overwrite(self.create_result_path))
            return False
        return True

    @staticmethod
    def filter_path(str):
        # return str.split('.')[0]
        # return str.strip(',.-\!"#¤%&/()=')
        return re.sub('[^A-Za-z0-9åäö_\-]+', '', str)

    def _on_change_template_export_file_name(self, *args):
        name = self.filter_path(self.template_export_file_name)
        self.template_export_file_name = name
        self._update_create_template_path()

    def _on_blur_template_export_file_name(self, *args):
        name = self.filter_path(self.template_export_file_name)
        if not name:
            name = hydrofia.get_default_template_path().stem
        self.template_export_file_name = name
        self._update_create_template_path()

    def _update_create_template_path(self):
        """Updates the template path related to the creation of template"""
        path = ''
        if self.template_export_file_name and self.template_directory:
            path = pathlib.Path(self.template_directory, self.template_export_file_name + '.xlsx')
        self.create_template_path = str(path)
        self._check_create_template_path_exists()

    def _on_change_result_file_name(self, *args):
        name = self.filter_path(self.result_file_name)
        self.result_file_name = name
        self._update_create_result_path()

    def _on_blur_result_file_name(self, *args):
        name = self.filter_path(self.result_file_name)
        if not name:
            if self.use_template_path:
                name = self.use_template_path.stem + '_result'
            else:
                name = ''
        self.result_file_name = name
        self._update_create_result_path()

    def _update_create_result_path(self):
        """Updates the template path related to the creation of template"""
        name = self.result_file_name
        template_path = self.use_template_path
        if not template_path:
            return
        directory = template_path.parent
        if not name:
            path = ''
        else:
            path = pathlib.Path(directory, name + '.xlsx')
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
        self._open_template_dir_btn.visible = True
        if not path:
            path = TEXTS.missing_template_directory
            self._open_template_dir_btn.visible = False
        self._open_template_dir_btn.update()
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
            if self.template_export_file_name and self.template_directory:
                path = pathlib.Path(self.template_directory, self.template_export_file_name + '.xlsx')
        self._create_template_path.value = str(path)
        self._create_template_path.update()

    @property
    def template_export_file_name(self) -> str:
        return self._template_export_file_name.value

    @template_export_file_name.setter
    def template_export_file_name(self, name=None):
        self._template_export_file_name.value = name
        self._template_export_file_name.update()

    @property
    def use_template_path(self) -> pathlib.Path | None:
        value = self._use_template_path.value
        if not value or value == TEXTS.missing_template_path:
            return None
        return pathlib.Path(value)

    @use_template_path.setter
    def use_template_path(self, path=None):
        self._open_template_file_btn.visible = True
        if not path:
            path = TEXTS.missing_template_path
            self._open_template_file_btn.visible = False
        self._open_template_file_btn.update()
        self._use_template_path.value = str(path)
        self._use_template_path.update()

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
            if self.result_file_name and self.use_template_path:
                path = pathlib.Path(self.use_template_path.parent, pathlib.Path(self.result_file_name).stem + '.xlsx')
        self._create_result_path.value = str(path)
        self._create_result_path.update()

    @property
    def result_file_name(self) -> str:
        return self._result_file_name.value

    @result_file_name.setter
    def result_file_name(self, path=None):
        self._result_file_name.value = path
        self._result_file_name.update()

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
    app = FletApp(log_in_console=log_in_console)
    return app
