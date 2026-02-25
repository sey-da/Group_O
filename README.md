# Group_O
# # Team Members
  - Sengul Seyda Yilmaz, 70549@novasbe.pt
  - Madalena Rocha, 72541@novasbe.pt
  - Nora Puchert, 73020@novasbe.pt
  - Margarida Parracho, 75108@novasbe.pt

## Project Description - Project Okavango

A lightweight environmental data analysis tool built during a two-day hackathon. The app visualizes deforestation, land protection, and land degradation data on an interactive world map using the most recent data available from [Our World in Data](https://ourworldindata.org).

## Project Structure

```
Group_O/
├── app/
│   ├── __init__.py
|   └── class_environment_data.py
│   └── data_handler.py
│   └── streamlit_app.py
├── downloads/
├── notebooks/
├── tests/
│   ├── test_download.py
│   └── test_merge.py
├── .gitignore
├── LICENSE.md
├── README.md
└── main.py
```

## Datasets

All datasets are downloaded automatically from [Our World in Data](https://ourworldindata.org) and [Natural Earth](https://www.naturalearthdata.com). 

| Dataset | Source |
|---|---|
| Annual change in forest area | Our World in Data |
| Annual deforestation | Our World in Data |
| Share of land that is protected | Our World in Data |
| Share of land that is degraded | Our World in Data |
| Forest area as share of land area | Our World in Data |
| World map (country boundaries) | Natural Earth 110m |

## Installation

### 1. Clone the repository

```bash
git clone <https://github.com/sey-da/Group_O.git>
cd Group_O
```

### 2. Create and activate a virtual environment

**Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install requests geopandas pandas pytest streamlit
```

## Usage

### Download datasets
```bash
python main.py
```
### Run the tests

```bash
python -m pytest
```

### Run the Streamlit app

```bash
python -m streamlit run app/streamlit_app.py
```

The app will open in your browser.

## Code Overview

### `app/data_handler.py`
Contains two functions:

**`download_datasets(download_dir)`**
Downloads all CSV datasets and the Natural Earth ZIP file into the specified directory. Returns a dictionary mapping dataset names to their local file paths.

**`merge_datasets(downloaded_files)`**
Merges each downloaded CSV dataset with the Natural Earth world map using GeoPandas. The GeoDataFrame is always the left dataframe in the merge to preserve geometry. Returns a dictionary of merged GeoDataFrames.

### `app/environment_data.py`
Contains a Pydantic configuration model and the main data management class:

**`EnvironmentConfig`**
A Pydantic model that validates the configuration passed to `EnvironmentData`. Ensures the downloads directory exists, creating it automatically if needed.

**`EnvironmentData`**
Central data manager for the project. On instantiation, automatically calls `download_datasets()` and `merge_datasets()`, then exposes the five resulting GeoDataFrames as named attributes (`annual_change_forest_area`, `annual_deforestation`, `share_land_protected`, `share_land_degraded`, `forest_area_total`). Also provides `list_available_maps()` which returns all GeoDataFrames as a named dictionary for use in the Streamlit app.

### `app/streamlit_app.py`
The main user-facing application:

**Dataset selector**
A dropdown that allows the user to select one dataset at a time to explore.

**World map**
A choropleth map of the selected dataset, with countries colored by value and grey for missing data.

**Country breakdown chart**
A chart tailored to each dataset — showing top gainers vs losers for change-based datasets, top 10 worst offenders for deforestation, and top 5 vs bottom 5 for share-based datasets.

### `tests/`

| File | What it tests |
|---|---|
| `test_download.py` | Files are downloaded, exist, are not empty, and are readable |
| `test_merge.py` | Merged results are GeoDataFrames with geometry and correct row count |

## Requirements

- Python 3.10+
- geopandas
- pandas
- requests
- pydantic
- streamlit
- matplotlib
- pytest

## License

See `LICENSE.md`.
