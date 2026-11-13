import pytest

m = {
    "timestamp": "PH-0521-001",
    "sampleName": "PH-0918-001",
    "action": "PH-0918-001",
}

@pytest.fixture
def write_export_file(tmp_path):
    """Return a function that writes a HydroFIA export file and returns its path."""

    def write(headers, rows):
        path = tmp_path / "export.txt"
        lines = [
            *(",".join(column for column in header) for header in headers),
            *(",".join(row) for row in rows),
        ]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    return write
