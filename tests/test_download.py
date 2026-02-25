"""Tests for the download function."""

from pathlib import Path
from app.data_handler import download_datasets


def test_download_creates_files(tmp_path):
    """Test that download_datasets creates all expected files."""
    files = download_datasets(download_dir=str(tmp_path))

    # Check all expected keys are present
    expected_keys = [
        "annual_change_forest_area",
        "annual_deforestation",
        "share_land_protected",
        "share_land_degraded",
        "forest_area_total",
        "geodata",
    ]
    for key in expected_keys:
        assert key in files, f"Missing dataset: {key}"

    # Check files actually exist and are not empty
    for name, path in files.items():
        assert path.exists(), f"File not found: {path}"
        assert path.stat().st_size > 0, f"File is empty: {path}"


def test_download_returns_correct_types(tmp_path):
    """Test that download_datasets returns a dict of Path objects."""
    files = download_datasets(download_dir=str(tmp_path))

    assert isinstance(files, dict)
    for name, path in files.items():
        assert isinstance(path, Path), f"{name} is not a Path object"


def test_download_csv_files_are_readable(tmp_path):
    """Test that downloaded CSV files can be read with pandas."""
    import pandas as pd

    files = download_datasets(download_dir=str(tmp_path))

    for name, path in files.items():
        if name == "geodata":
            continue  # Skip ZIP file
        df = pd.read_csv(path)
        assert len(df) > 0, f"CSV is empty: {name}"
        assert len(df.columns) > 0, f"CSV has no columns: {name}"