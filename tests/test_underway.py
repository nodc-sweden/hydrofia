import pandas as pd
import pytest

from hydrofia.errors import InvalidHydrofiaFileError
from hydrofia.underway import read_underway_file, calculate_ph_tot_labt_p0

UNDERWAY_COLUMNS = (
    "timestamp",
    "sampleName",
    "action",
    "salinity",
    "temperatureSample",
    "R0",
    "serialIndicator",
    "absorbance434",
    "absorbance487",
    "absorbance578",
)


def make_row(sample_name, action):
    return [
        "2025-07-14T13:34:37",
        sample_name,
        action,
        "26.75",
        "25.232",
        "0.628344",
        "CMCP-1021-001",
        "0.395652",
        "0.299198",
        "0.501930",
    ]


def test_read_underway_file_keeps_continuous_and_discrete_rows(write_export_file):
    # Given an export file with both continuous and discrete measurements
    given_path = write_export_file(
        [
            [f"kod-{n:02}" for n, _ in enumerate(UNDERWAY_COLUMNS)],
            UNDERWAY_COLUMNS,
            ["[]"] * len(UNDERWAY_COLUMNS),
        ],
        [
            make_row("B", "Measure continuous"),
            make_row("A", "Measure discrete"),
            make_row("C", "Measure continuous"),
        ],
    )

    # When reading the file
    data = read_underway_file(given_path)

    # Then both rows are kept, in file order
    assert list(data["sampleName"]) == ["B", "A", "C"]
    assert list(data["action"]) == ["Measure continuous", "Measure discrete", "Measure continuous"]


@pytest.mark.parametrize(
    "given_missing_column",
    (
        "salinity",
        "temperatureSample",
        "R0",
        "serialIndicator",
        "absorbance434",
        "absorbance487",
        "absorbance578",
    ),
)
def test_read_underway_file_raises_for_missing_underway_column(
    write_export_file, given_missing_column
):
    # Given an export file without one of the columns underway needs
    header = list(UNDERWAY_COLUMNS)
    row = make_row("A", "Measure continuous")
    missing_index = header.index(given_missing_column)
    del header[missing_index]
    del row[missing_index]
    given_path = write_export_file(header, [row])

    # When reading the file
    # Then an InvalidHydrofiaFileError is raised
    with pytest.raises(InvalidHydrofiaFileError):
        read_underway_file(given_path)


def test_calculate_ph_tot_labt_p0():
    # Given underway data
    given_data = pd.DataFrame(
        [
            [
                "2025-07-14T13:34:37",
                "A",
                "Measure continuous",
                "26.75",
                "25.232",
                "0.628344",
                "CMCP-1021-001",
                "0.395652",
                "0.299198",
                "0.501930",
            ],
            [
                "2025-07-14T13:35:37",
                "B",
                "Measure continuous",
                "26.75",
                "25.232",
                "0.628344",
                "CMCP-1021-001",
                "0.395652",
                "0.299198",
                "0.501930",
            ],
        ],
        columns=UNDERWAY_COLUMNS,
    )

    # When calculating
    calculated_data = calculate_ph_tot_labt_p0(given_data)

    # Then the column "pH-tot-labT-P0" is added
    assert "ph-tot-labT-P0" in calculated_data
