"""
Data download and processing functions for Project Okavango.
"""

import requests
from pathlib import Path


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