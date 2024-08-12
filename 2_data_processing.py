import os
import json
import pandas as pd
from datetime import datetime
import numpy as np
from tqdm import tqdm

MYDATAPATH = "dwd_weather_data"
TEMPERATURE_THRESHOLD = 35  # temperature threshold in Celsius

geojson_files = [f for f in os.listdir(MYDATAPATH) if f.endswith(".geojson")]
temp_dir = os.path.join(MYDATAPATH, "temp")
os.makedirs(temp_dir, exist_ok=True)


def process_geojson(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    features = data["data"]["features"]
    combined_data = []

    for feature in features:
        station_id = feature["properties"]["id"]
        geometry = json.dumps(feature["geometry"])
        properties = feature["properties"]

        for value in feature["values"]:
            combined_value = {
                "id": station_id,
                "geometry": geometry,
                "name": properties["name"],
                "state": properties["state"],
                "start_date": properties["start_date"],
                "end_date": properties["end_date"],
                "date": value["date"],
                "value": value["value"],
            }
            combined_data.append(combined_value)

    return pd.DataFrame(combined_data)


def process_and_save_chunk(chunk, output_file):
    chunk["value"] = pd.to_numeric(chunk["value"], errors="coerce")
    chunk = chunk.dropna(subset=["value"])
    chunk["value"] = chunk["value"] - 273.15
    chunk["date"] = pd.to_datetime(chunk["date"])
    chunk["year"] = chunk["date"].dt.year
    chunk = chunk.sort_values(["date", "id"])
    chunk.to_json(output_file, orient="records", lines=True, date_format="iso")


# Process each file and save as temporary JSON
# Process each file and save as temporary JSON
temp_files = []
for file in tqdm(geojson_files, desc="Processing GeoJSON files"):
    temp_file = os.path.join(temp_dir, f"temp_{file.replace('.geojson', '.json')}")

    # Add this line to check if the file already exists
    if not os.path.exists(temp_file):
        df = process_geojson(os.path.join(MYDATAPATH, file))
        process_and_save_chunk(df, temp_file)

    temp_files.append(temp_file)


# Combine temporary files and aggregate
def aggregate_with_metadata(group):
    metadata = group.iloc[0]
    n_days = np.sum(group["value"] >= TEMPERATURE_THRESHOLD)
    return pd.Series(
        {
            "n_days": n_days,
            "geometry": metadata["geometry"],
            "name": metadata["name"],
            "state": metadata["state"],
        }
    )


station_data_per_year = pd.DataFrame()
# Combine temporary files and aggregate
for temp_file in tqdm(temp_files, desc="Aggregating data"):
    chunk = pd.read_json(temp_file, lines=True)
    try:
        # Add this line to print column names for debugging
        print(f"Columns in {temp_file}: {chunk.columns}")

        aggregated = (
            chunk.groupby(["id", "year"]).apply(aggregate_with_metadata).reset_index()
        )
        station_data_per_year = pd.concat(
            [station_data_per_year, aggregated], ignore_index=True
        )
    except KeyError as e:
        print(f"Error processing file: {temp_file}")
        print(f"KeyError: {e}")
        # Optionally, print the first few rows of the problematic file
        print(chunk.head())
        # You might want to continue with the next file instead of breaking the loop
        continue

station_data_per_year["n_days"] = station_data_per_year["n_days"].fillna(0)
station_data_per_year = station_data_per_year.rename(columns={"id": "Stations_id"})

# Save the final result
output_file = os.path.join(MYDATAPATH, "station_data_per_year.json")
station_data_per_year.to_json(output_file, orient="records", lines=True)

print(f"Data saved to {output_file}")

# Clean up temporary files
for temp_file in temp_files:
    os.remove(temp_file)
os.rmdir(temp_dir)
