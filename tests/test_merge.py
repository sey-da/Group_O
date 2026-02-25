"""Tests for the merge function."""

import geopandas as gpd
from app.data_handler import download_datasets, merge_datasets


def test_merge_returns_geodataframes(tmp_path):
    """Test that merge_datasets returns GeoDataFrames with geometry."""
    files = download_datasets(download_dir=str(tmp_path))
    merged = merge_datasets(files)

    for name, gdf in merged.items():
        assert isinstance(gdf, gpd.GeoDataFrame), f"{name} is not a GeoDataFrame"
        assert "geometry" in gdf.columns, f"{name} missing geometry column"
        assert len(gdf) > 0, f"{name} is empty"