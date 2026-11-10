import numpy as np
import numpy.typing as npt

from hydrofia.ext_src import seacarb

KELVIN_OFFSET = 273.15


def calculate_ph_t_spec(
    salinity: npt.ArrayLike, temperature: npt.ArrayLike, r0: npt.ArrayLike
) -> float | np.ndarray:
    salinity, temperature, r0 = (
        np.asarray(value, dtype=float) for value in (salinity, temperature, r0)
    )
    has_input = (salinity != 0) & (temperature != 0) & (r0 != 0)
    # Measurements that give a negative logarithm argument end up as NaN
    with np.errstate(invalid="ignore", divide="ignore"):
        ph = seacarb.pHTspec(salinity, temperature + KELVIN_OFFSET, r0, "mueller")
    ph = np.where(has_input, ph, np.nan)
    return float(ph) if ph.ndim == 0 else ph
