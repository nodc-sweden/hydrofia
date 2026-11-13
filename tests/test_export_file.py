import pytest

from hydrofia.errors import InvalidHydrofiaFileError
from hydrofia.export_file import read_export_file

REQUIRED_COLUMNS = ("timestamp", "sampleName", "action")


def test_read_export_file_returns_data_rows_in_file_order(write_export_file):
    # Given an export file with two data rows
    given_path = write_export_file(
        [
            ["PH-0521-001", "PH-0918-001", "PH-0918-001"],
            ["timestamp", "sampleName", "action"],
        ],
        [
            ["2025-07-14T13:36:50", "B", "Measure continuous"],
            ["2025-07-14T13:34:37", "A", "Measure discrete"],
        ],
    )

    # When reading the file
    data = read_export_file(given_path, REQUIRED_COLUMNS)

    # Then all data rows are returned in file order
    assert list(data.columns) == ["timestamp", "sampleName", "action"]
    assert list(data["sampleName"]) == ["B", "A"]


def test_read_export_file_raises_for_binary_file(tmp_path):
    # Given a file that is not text
    given_path = tmp_path / "export.txt"
    given_path.write_bytes(b"\xff\xfe\x00\x01")

    # When reading the file
    # Then an InvalidHydrofiaFileError is raised
    with pytest.raises(InvalidHydrofiaFileError):
        read_export_file(given_path, REQUIRED_COLUMNS)


@pytest.mark.skip
def test_read_export_file_raises_for_too_few_lines(tmp_path):
    # Given a file with only the first line and the header
    given_path = tmp_path / "export.txt"
    given_path.write_text("PH-0521-001\ntimestamp,sampleName,action\n", encoding="utf-8")

    # When reading the file
    # Then an InvalidHydrofiaFileError is raised
    with pytest.raises(InvalidHydrofiaFileError):
        read_export_file(given_path, REQUIRED_COLUMNS)


@pytest.mark.skip
def test_read_export_file_raises_for_missing_required_column(write_export_file):
    # Given an export file without the action column
    given_path = write_export_file(
        [
            ["PH-0521-001", "PH-0918-001"],
            ["timestamp", "sampleName"]
        ],
        [["2025-07-14T13:34:37", "A"]],
    )

    # When reading the file
    # Then an InvalidHydrofiaFileError is raised
    with pytest.raises(InvalidHydrofiaFileError):
        read_export_file(given_path, REQUIRED_COLUMNS)

@pytest.mark.skip
def test_read_export_file_raises_when_rows_do_not_match_header(write_export_file):
    # Given an export file with a data row that has one value too many
    given_path = write_export_file(
        [
            ["PH-0521-001", "PH-0918-001", "PH-0918-001"],
            ["timestamp", "sampleName", "action"],
        ],
        [["2025-07-14T13:34:37", "A", "Measure discrete", "extra"]],
    )

    # When reading the file
    # Then an InvalidHydrofiaFileError is raised
    with pytest.raises(InvalidHydrofiaFileError):
        read_export_file(given_path, REQUIRED_COLUMNS)
