import numpy as np
import pandas as pd
import pytest

from hydrofia import crm
from hydrofia.reference_batch import ReferenceBatches

GIVEN_BATCH_DATA = {
    "195": {
        "NB": "A",
        "alk": "2213.51",
        "batch_nr": "Batch  195",
        "bottling_date": "Match 20, 2013",
        "dic": "2024.96",
        "phosphate": "0.49",
        "salinity": "33.485",
        "silicate": "3.6",
    },
    "209": {
        "NB": "G",
        "alk": "2210.40",
        "batch_nr": "Batch  209",
        "bottling_date": "July 2, 2016",
        "dic": "2060.05",
        "phosphate": "0.50",
        "salinity": "33.147",
        "silicate": "3.8",
    },
}


@pytest.fixture
def given_batches(tmp_path, monkeypatch):
    """Fixed batches so the test does not depend on NOAA or the network."""
    # ReferenceBatches writes batches.yaml to the working directory when created
    monkeypatch.chdir(tmp_path)

    batches = ReferenceBatches.from_dict(GIVEN_BATCH_DATA)
    monkeypatch.setattr(crm, "BATCHES", batches)
    return batches


@pytest.mark.parametrize(
    "given_rows, expected_rows",
    (
        (
            [("CRM-195", 25.0, 7.870)],
            {0: (7.8609227554, 0.0090772446)},
        ),  # Single CRM row
        (
            [("CRM-195", 24.8, 7.860), ("CRM-209", 25.1, 7.780)],
            {
                0: (7.8638468861, -0.0038468861),
                1: (7.7748018522, 0.0051981478),
            },
        ),  # Two batches
        (
            [
                ("CRM-195", 24.8, 7.860),
                ("Sample-1", 25.0, 8.000),
                ("CRM-209", 25.1, 7.780),
                ("CMR-195", 25.3, 7.850),
                ("ICOS-CRM-209", 25.0, 8.000),
                ("crm-209", 24.9, 7.775),
            ],
            {
                0: (7.8638468861, -0.0038468861),
                2: (7.7748018522, 0.0051981478),
                3: (7.8565407425, -0.0065407425),
                5: (7.7776693654, -0.0026693654),
            },
        ),  # CRM rows mixed with other rows
        (
            [("Sample-1", 25.0, 8.000), ("ICOS-CRM-209", 25.0, 8.000)],
            {},
        ),  # No CRM rows
    ),
)
def test_calculate_crm_vectorized(given_batches, given_rows, expected_rows):
    # Given a dataframe with HydroFIA rows
    given_data = pd.DataFrame(
        given_rows, columns=["sampleName", "temperatureSample", "pH-tot-labT-P0"]
    )

    # When the reference pH is calculated
    result = crm.calculate_crm(given_data)

    # Then only the CRM rows are kept, with their original index
    assert list(result.index) == list(expected_rows)

    if not expected_rows:
        return

    # And each row gets the expected reference pH and difference
    expected_reference_ph = [reference for reference, _ in expected_rows.values()]
    expected_difference = [difference for _, difference in expected_rows.values()]
    np.testing.assert_allclose(
        result["reference-pH"].astype(float), expected_reference_ph, rtol=0, atol=1e-9
    )
    np.testing.assert_allclose(
        result["pH-difference"].astype(float), expected_difference, rtol=0, atol=1e-9
    )
