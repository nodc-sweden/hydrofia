import pathlib

from hydrofia.calculate import Calculate
from hydrofia.ctd import CtdStandardFormatCollection
from hydrofia import exporter
from hydrofia.exporter import ExporterTxt
from hydrofia.exporter import ExporterXlsxResultFile
from hydrofia.hydrofia import HydrofiaExportFileDiscrete
from hydrofia.hydrofia import HyrdofiaExcelTemplate
from hydrofia import utils


def get_default_template_path(directory: pathlib.Path | str = None) -> pathlib.Path:
    return HyrdofiaExcelTemplate.get_default_template_path(directory)


def create_template(template_path: pathlib.Path | str = None,
                    hydrofia_export_path: pathlib.Path | str = None,
                    overwrite: bool = False,
                    year: int = None,
                    month: int = None):
    start_date, end_date = utils.get_date_limits_from_year_and_month(year=year, month=month)
    template = HyrdofiaExcelTemplate(template_path)
    hf = HydrofiaExportFileDiscrete(hydrofia_export_path)
    hf.filter_data_by_date(start_date=start_date, end_date=end_date)
    return template.create_template(hf, overwrite=overwrite)


def get_id_string_for_hydrofia_export_file(path: pathlib.Path | str = None,
                                           year: int = None,
                                           month: int = None):
    start_date, end_date = utils.get_date_limits_from_year_and_month(year=year, month=month)
    hf = HydrofiaExportFileDiscrete(path)
    hf.filter_data_by_date(start_date=start_date, end_date=end_date)
    info = hf.get_info()
    if not info:
        return
    stem = f"{info['year_string']}_{info['from_serno']}_{info['to_serno']}"
    return stem


def get_calculated_object(
        template_path: pathlib.Path | str = None,
        ctd_directory: pathlib.Path | str = None,
        **kwargs):
    """Returns a Calculate object calculated with info from template and ctd_directory"""
    template = HyrdofiaExcelTemplate(template_path)
    ctd_obj = CtdStandardFormatCollection(ctd_directory,
                                          max_depth_diff_allowed=kwargs.get('max_depth_diff_allowed'),
                                          surface_layer_depth=kwargs.get('surface_layer_depth'),
                                          bottom_layer_depth=kwargs.get('bottom_layer_depth'),
                                          )
    calc = Calculate(hydrofia_data=template,
                     salinity_and_temp_data=ctd_obj)
    calc.calculate()
    return calc


def create_xlsx_result_file_from_calc_object(
        calc_object: Calculate = None,
        path: pathlib.Path | str = None,
        overwrite: bool = False,
        **kwargs
        ):

    xlsx_exporter = ExporterXlsxResultFile(path, overwrite=overwrite)
    calc_object.save_data(xlsx_exporter, overwrite=overwrite, **kwargs)


def create_txt_archive_file_from_calc_object(
        calc_object: Calculate = None,
        path: pathlib.Path | str = None,
        overwrite: bool = False,
        **kwargs
):
    txt_exporter = ExporterTxt(path, overwrite=overwrite)
    calc_object.save_data(txt_exporter, overwrite=overwrite, **kwargs)


def create_xlsx_result_file(template_path: pathlib.Path | str = None,
                            ctd_directory: pathlib.Path | str = None,
                            result_file_path: pathlib.Path | str = None,
                            overwrite: bool = False,
                            **kwargs):
    
    calc = get_calculated_object(
        template_path=template_path, 
        ctd_directory=ctd_directory, 
        **kwargs)
    create_xlsx_result_file_from_calc_object(
        calc_object=calc,
        path=result_file_path,
        overwrite=overwrite,
        **kwargs
    )



def get_exporter_list():
    return exporter.Exporters().get_exporter_list()

