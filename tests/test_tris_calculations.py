import numpy as np
import pandas as pd
import pytest

from hydrofia.tris import (
    calculate_ph_tris_dickson,
    calculate_ph_tris_lne_7_612,
    calculate_ph_tris_lne_8_091,
)


@pytest.mark.parametrize(
    "given_temperature, expected_ph",
    (
        (24.5, 8.10917852),
        (24.75, 8.10135896),
        (25, 8.09354909),
        (25.25, 8.08574887),
        (25.5, 8.07795823),
    ),
)
def test_calculate_ph_tris_dickson(given_temperature, expected_ph):
    given_salinity = 35
    given_temperature_k = given_temperature + 273.15
    calculated_ph = calculate_ph_tris_dickson(given_salinity, given_temperature_k)

    assert f"{calculated_ph:.3f}" == f"{expected_ph:.3f}"


def test_calculate_ph_tris_dickson_on_array():
    given_salinity = 35
    given_temperature = pd.Series((24.5, 24.75, 25, 25.25, 25.5))

    given_temperature += 273.15
    calculated_ph = calculate_ph_tris_dickson(given_salinity, given_temperature)
    expected_ph = pd.Series((8.10917852, 8.10135896, 8.09354909, 8.08574887, 8.07795823))
    np.testing.assert_allclose(calculated_ph, expected_ph, atol=1e-8)


@pytest.mark.parametrize(
    "given_temperature, expected_ph",
    (
        (24.5, 7.628),
        (24.75, 7.62),
        (25, 7.612),
        (25.25, 7.604),
        (25.5, 7.596),
    ),
)
def test_calculate_ph_tris_lne_7_612(given_temperature, expected_ph):
    calculated_ph = calculate_ph_tris_lne_7_612(given_temperature)
    assert f"{calculated_ph:.3f}" == f"{expected_ph:.3f}"


@pytest.mark.parametrize(
    "given_temperature, expected_ph",
    (
        (24.5, 8.107),
        (24.75, 8.099),
        (25, 8.091),
        (25.25, 8.083),
        (25.5, 8.075),
    ),
)
def test_calculate_ph_tris_lne_8_091(given_temperature, expected_ph):
    calculated_ph = calculate_ph_tris_lne_8_091(given_temperature)
    assert f"{calculated_ph:.3f}" == f"{expected_ph:.3f}"
