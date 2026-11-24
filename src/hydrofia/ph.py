import numpy as np
import pandas as pd

from hydrofia.constants import KELVIN_OFFSET, TRIS_SALINITY
from hydrofia.ext_src import seacarb


def calculate_ph_tot_labt_p0(data: pd.DataFrame) -> pd.DataFrame:
    salinity = data["salinity"]
    salinity[data["sampleName"].str.contains("TRIS", case=False, na=False)] = (
        TRIS_SALINITY
    )

    data["pH-tot-labT-P0"] = calculate_ph_t_spec(
        salinity,
        data["temperatureSample"],
        data["R0"],
    )
    return data


def calculate_ph_t_spec(
    salinity: float | pd.Series, temperature: float | pd.Series, r0: float | pd.Series
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
