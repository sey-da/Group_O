from app.data_handler import download_datasets
from app.class_environment_data import EnvironmentData

files = download_datasets()
print(files)


data = EnvironmentData()
maps = data.list_available_maps()

for name, gdf in maps.items():
    print(name, "→", len(gdf), "rows")
