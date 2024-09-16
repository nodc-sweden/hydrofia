import datetime
import calendar
import os
import platform
import subprocess

SHIP_MAPPER = {
    # '7710': '77SE'
}


def map_ship(ship):
    return SHIP_MAPPER.get(ship, ship)


def open_file_in_default_program(path):
    if platform.system() == 'Darwin':  # macOS
        subprocess.call(('open', str(path)))
    elif platform.system() == 'Windows':  # Windows
        os.startfile(str(path))
    else:  # linux variants
        subprocess.call(('xdg-open', str(path)))


def get_date_limits_from_year_and_month(year: int = None, month: int = None):
    today = datetime.datetime.now()
    year = year or today.year
    if not month:
        return datetime.datetime(year, 1, 1).date(), datetime.datetime(year, 12, 31).date()
    if month < 1 or month > 12:
        raise ValueError('Month must be between 1 and 12')
    start_date = datetime.datetime(year, month, 1).date()
    end_date = datetime.datetime(year, month, calendar.monthrange(year, month)[1]).date()
    return start_date, end_date




