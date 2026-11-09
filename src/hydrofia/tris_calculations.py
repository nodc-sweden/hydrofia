from typing import Any

import numpy as np


def calculate_ph_tris_dickson(salinity: int, termperature_k: float) -> Any:
    return (
        (11911.08 - 18.2499 * salinity - 0.039336 * salinity**2) / termperature_k
        + (-366.27059 + 0.53993607 * salinity + 0.00016329 * salinity**2)
        + (64.52243 - 0.084041 * salinity) * np.log(termperature_k)
        - 0.11149858 * termperature_k
    )


def calculate_ph_tris_lne_7_612(temperature_c: float):
    return 7.612 + 0.032 * (25 - temperature_c)


def calculate_ph_tris_lne_8_091(temperature_c: float):
    return 8.091 + 0.032 * (25 - temperature_c)


TRIS_SALINITY = 35

TRIS_BUFFERS = {
    "TRIS_Dickson": lambda temperature_c: calculate_ph_tris_dickson(
        TRIS_SALINITY, temperature_c + 273.15
    ),
    "TRIS_LNE_7.612": calculate_ph_tris_lne_7_612,
    "TRIS_LNE_8.091": calculate_ph_tris_lne_8_091,
}
