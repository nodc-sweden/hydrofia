import numpy as np
import pandas as pd
import pytest

from hydrofia.calculate import Calculate


class FakeHydrofiaData:
    def __init__(self, data: pd.DataFrame):
        self._data = data

    def get_data(self) -> pd.DataFrame:
        return self._data


class FakeCtdData:
    def __init__(self, salt_by_serno: dict[str, float]):
        self._salt_by_serno = salt_by_serno

    def get_ctd_data(self, year=None, ship=None, serno=None, depth=None) -> dict:
        if serno not in self._salt_by_serno:
            return {}
        return {"salt": self._salt_by_serno[serno], "temp": 10.0}


def test_calculate_uses_ctd_salinity_and_gives_nan_when_ctd_is_missing():
    # Given one sample with CTD data and one without
    given_hydrofia_data = FakeHydrofiaData(
        pd.DataFrame(
            {
                "serno": ["0001", "0002"],
                "depth": ["5", "5"],
                "year": ["2025", "2025"],
                "country": ["77", "77"],
                "ship": ["SE", "SE"],
                "salinity": ["0", "0"],
                "temperatureSample": ["25.232", "25.232"],
                "R0": ["0.628344", "0.628344"],
            }
        )
    )
    given_ctd_data = FakeCtdData({"0001": 26.75})

    # When calculating
    calc = Calculate(given_hydrofia_data, given_ctd_data)
    calc.calculate()

    # Then the CTD sample gets pH and the sample without CTD gets nan
    calculated_ph = calc.data["pH-tot-labT-P0"]
    ph_with_ctd, ph_without_ctd = calculated_ph
    assert ph_with_ctd == pytest.approx(7.471469, abs=1e-6)
    assert np.isnan(ph_without_ctd)
