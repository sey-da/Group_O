"""
EnvironmentData: Central data management class for Project Okavango.

Handles dataset downloading, merging with geographical data,
and exposes clean GeoDataFrames as attributes for the Streamlit app.
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
from pydantic import BaseModel, field_validator

from app.data_handler import download_datasets, merge_datasets

class EnvironmentConfig(BaseModel):
    """
    Configuration for EnvironmentData.

    Attributes:
        downloads_dir: Folder where datasets will be saved.
                       Created automatically if it does not exist.
    """

    downloads_dir: Path = Path("downloads")

    @field_validator("downloads_dir")
    @classmethod
    def ensure_directory_exists(cls, v: Path) -> Path:
        """Create the downloads directory if it does not exist yet."""
        v.mkdir(parents=True, exist_ok=True)
        return v


# ─────────────────────────────────────────────────────────────
# MAIN CLASS
# ─────────────────────────────────────────────────────────────

class EnvironmentData:
    """
    Central data manager for Project Okavango.

    On instantiation this class automatically:
      1. Downloads all datasets into the downloads directory.
      2. Merges each dataset with the Natural Earth world map.
      3. Exposes the five resulting GeoDataFrames as attributes.

    Attributes:
        config (EnvironmentConfig): Configuration used by this instance.
        annual_change_forest_area (gpd.GeoDataFrame): Annual change in forest area.
        annual_deforestation (gpd.GeoDataFrame): Annual deforestation figures.
        share_land_protected (gpd.GeoDataFrame): Share of land that is protected.
        share_land_degraded (gpd.GeoDataFrame): Share of land that is degraded.
        forest_area_total (gpd.GeoDataFrame): Forest area as share of total land.

    Example:
        >>> data = EnvironmentData()
        >>> data.annual_change_forest_area.head()
    """

    def __init__(self, config: EnvironmentConfig | None = None) -> None:
        """
        Initialize EnvironmentData.

        Runs download_datasets() and merge_datasets() automatically.

        Args:
            config: Optional EnvironmentConfig. Uses defaults if not provided.
        """

        # If no config is passed, use the defaults
        self.config: EnvironmentConfig = config or EnvironmentConfig()

        # Step 1 — Download all datasets
        # Returns: dict[str, Path] e.g. {"annual_change_forest_area": Path("downloads/annual_change_forest_area.csv"), ...}
        print("Downloading datasets...")
        self._downloaded_files: dict[str, Path] = download_datasets(
            download_dir=str(self.config.downloads_dir)
        )

        # Step 2 — Merge all datasets with the world map
        # Returns: dict[str, GeoDataFrame]
        print("Merging with world map...")
        self._merged: dict[str, gpd.GeoDataFrame] = merge_datasets(self._downloaded_files)

        # Step 3 — Expose each GeoDataFrame as a named attribute
        # This way the Streamlit app can do data.annual_deforestation
        # instead of data._merged["annual_deforestation"]
        self.annual_change_forest_area: gpd.GeoDataFrame = self._merged["annual_change_forest_area"]
        self.annual_deforestation: gpd.GeoDataFrame = self._merged["annual_deforestation"]
        self.share_land_protected: gpd.GeoDataFrame = self._merged["share_land_protected"]
        self.share_land_degraded: gpd.GeoDataFrame = self._merged["share_land_degraded"]
        self.forest_area_total: gpd.GeoDataFrame = self._merged["forest_area_total"]

        print("EnvironmentData is ready.")

    def list_available_maps(self) -> dict[str, gpd.GeoDataFrame]:
        """
        Return all GeoDataFrames as a named dictionary.

        Used by the Streamlit app to populate the map selector dropdown.

        Returns:
            Dict mapping human-readable names to their GeoDataFrames.

        Example:
            >>> data = EnvironmentData()
            >>> maps = data.list_available_maps()
            >>> selected = maps["Annual Deforestation"]
        """
        return {
            "Annual Change in Forest Area": self.annual_change_forest_area,
            "Annual Deforestation": self.annual_deforestation,
            "Share of Land Protected": self.share_land_protected,
            "Share of Land Degraded": self.share_land_degraded,
            "Forest Area Total Share": self.forest_area_total,
        }