import calendar
import datetime
import os
import platform
import subprocess

from hydrofia.errors import InvalidDateError

SHIP_MAPPER = {
    # '7710': '77SE'
}


def map_ship(ship):
    return SHIP_MAPPER.get(ship, ship)


def open_file_in_default_program(path):
    if platform.system() == "Darwin":  # macOS
        subprocess.call(("open", str(path)))
    elif platform.system() == "Windows":  # Windows
        os.startfile(str(path))
    else:  # linux variants
        subprocess.call(("xdg-open", str(path)))


def get_date_limits_from_year_and_month(
    year: int | None = None, month: int | None = None
) -> tuple[datetime.date, datetime.date]:
    year = year or datetime.date.today().year
    if not month:
        return datetime.date(year, 1, 1), datetime.date(year, 12, 31)
    try:
        last_day = calendar.monthrange(year, month)[1]
    except ValueError as e:
        raise InvalidDateError(f"Invalid month: {month}") from e
    return datetime.date(year, month, 1), datetime.date(year, month, last_day)
