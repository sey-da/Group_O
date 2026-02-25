"""
Data download and processing functions for Project Okavango.
"""

import requests
from pathlib import Path
import geopandas as gpd
import pandas as pd


# Dataset URLs from Our World in Data
DATASET_URLS: dict[str, str] = {
    "annual_change_forest_area": "https://ourworldindata.org/grapher/annual-change-forest-area.csv?v=1&csvType=full&useColumnShortNames=true",
    "annual_deforestation": "https://ourworldindata.org/grapher/annual-deforestation.csv?v=1&csvType=full&useColumnShortNames=true",
    "share_land_protected": "https://ourworldindata.org/grapher/terrestrial-protected-areas.csv?v=1&csvType=full&useColumnShortNames=true",
    "share_land_degraded": "https://ourworldindata.org/grapher/forest-area-net-change-rate.csv?v=1&csvType=full&useColumnShortNames=true",
    "forest_area_total": "https://ourworldindata.org/grapher/forest-area-as-share-of-land-area.csv?v=1&csvType=full&useColumnShortNames=true",
}

GEODATA_URL: str = (
    "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
)


def download_datasets(download_dir: str = "downloads") -> dict[str, Path]:
    """
    Download all required datasets into the downloads directory.

    Downloads CSV datasets from Our World in Data and the Natural Earth
    shapefile (as ZIP) for country boundaries.

    Args:
        download_dir: Path to the directory where files will be saved.

    Returns:
        Dictionary mapping dataset names to their local file paths.
    """
    output_dir = Path(download_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    downloaded_files: dict[str, Path] = {}

    # Download CSV files
    for name, url in DATASET_URLS.items():
        file_path = output_dir / f"{name}.csv"
        print(f"Downloading {name}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        file_path.write_bytes(response.content)
        downloaded_files[name] = file_path

    # Download geodata as ZIP for geopandas
    geo_path = output_dir / "ne_110m_admin_0_countries.zip"
    print("Downloading Natural Earth geodata...")
    response = requests.get(GEODATA_URL, timeout=30)
    response.raise_for_status()
    geo_path.write_bytes(response.content)
    downloaded_files["geodata"] = geo_path

    return downloaded_files



def merge_datasets(downloaded_files: dict[str, Path]) -> dict[str, gpd.GeoDataFrame]:
    """
    Merge the downloaded CSV datasets with the Natural Earth world map.

    The geopandas GeoDataFrame is always the left dataframe in the merge
    to preserve geometry information. Country names are standardized
    before merging to maximize matches.

    Args:
        downloaded_files: Dictionary mapping dataset names to their local
                          file paths, as returned by download_datasets().

    Returns:
        Dictionary mapping dataset names to merged GeoDataFrames.
    """
    # Load the world map from the ZIP file
    world = gpd.read_file(str(downloaded_files["geodata"]))

    # Standardize country name column for merging
    world["NAME"] = world["NAME"].str.strip()

    merged: dict[str, gpd.GeoDataFrame] = {}

    # All dataset keys except geodata
    dataset_keys = [key for key in downloaded_files if key != "geodata"]

    for name in dataset_keys:
        df = pd.read_csv(downloaded_files[name])

    # Normalize all column names to title case first
        df.columns = [col.strip().title() for col in df.columns]

    # Our World in Data uses "Entity" for country names 
        if "Entity" in df.columns:
            df = df.rename(columns={"Entity": "NAME"})

        df["NAME"] = df["NAME"].str.strip()

        if "Year" in df.columns:
            df = df[df["Year"] == df["Year"].max()]

        # Merge: world (left) with dataset (right)
            merged[name] = world.merge(df, on="NAME", how="left")

    return merged