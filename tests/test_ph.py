import numpy as np
import pandas as pd
import pytest

from hydrofia.ph import calculate_ph_t_spec


@pytest.mark.parametrize(
    "given_salinity, given_temperature, given_r0, expected_ph",
    (
        (23.4, 24.854, 0.066987, 6.466906),
        (26.73, 26.104, 0.196454, 6.936125),
        (26.75, 25.232, 0.628344, 7.471469),
    ),
)
def test_calculate_ph_t_spec_for_single_values(
    given_salinity, given_temperature, given_r0, expected_ph
):
    # Given salinity, temperature and r0
    # When calculating pH
    calculated_ph = calculate_ph_t_spec(given_salinity, given_temperature, given_r0)

    # Then the expected result is returned
    assert calculated_ph == pytest.approx(expected_ph, abs=1e-6)


def test_calculate_ph_t_spec_for_columns():
    # Given series with salinity, temperature and r0
    given_salinity = pd.Series([23.4, 26.73, 26.75])
    given_temperature = pd.Series([24.854, 26.104, 25.232])
    given_r0 = pd.Series([0.066987, 0.196454, 0.628344])

    # When calculating pH
    calculated_ph = calculate_ph_t_spec(given_salinity, given_temperature, given_r0)

    # Then the expected result is returned
    expected_ph = [6.466906, 6.936125, 7.471469]
    np.testing.assert_allclose(calculated_ph, expected_ph, atol=1e-6)


@pytest.mark.parametrize(
    "given_salinity, given_temperature, given_r0",
    (
        (np.nan, 25.0, 0.5),
        (30.0, np.nan, 0.5),
        (30.0, 25.0, np.nan),
        (0.0, 25.0, 0.5),
        (30.0, 0.0, 0.5),
        (30.0, 25.0, 0.0),
    ),
)
def test_calculate_ph_t_spec_is_nan_for_missing_or_zero_input(
    given_salinity, given_temperature, given_r0
):
    # Given salinity, temperature and r0 where at least one value is 0 or nan
    given_values = (given_salinity, given_temperature, given_r0)
    any_zero_value = any(x == 0 for x in given_values)
    any_nan_value = any(np.isnan(x) for x in given_values)
    assert any_zero_value or any_nan_value

    # When calculating pH
    calculated_ph = calculate_ph_t_spec(given_salinity, given_temperature, given_r0)

    # Then the result is nan
    assert np.isnan(calculated_ph)
