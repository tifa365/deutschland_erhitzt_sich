import os
import pandas as pd
from wetterdienst import Resolution, Period
from wetterdienst.provider.dwd.observation import (
    DwdObservationRequest,
    DwdObservationDataset,
)

# Define constants
TEMPERATURE_THRESHOLD = 35  # Temperature threshold in Celsius
START_DATE = "1963-12-31"
END_DATE = "2023-12-31"
OUTPUT_FOLDER = "dwd_weather_data"
GEOJSON_FILENAME = "all_stations_data.geojson"

# Ensure the output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Create the request for climate summary data (includes max temperature)
request = DwdObservationRequest(
    parameter=DwdObservationDataset.CLIMATE_SUMMARY,
    resolution=Resolution.DAILY,
    period=Period.HISTORICAL,
    start_date=START_DATE,
    end_date=END_DATE,
)

# Get all stations
stations = request.all()

# Fetch all values for all stations
values = stations.values.all()

# Convert to GeoJSON with metadata
geojson_data = values.to_geojson(with_metadata=True)

# Save GeoJSON data to a file
geojson_filepath = os.path.join(OUTPUT_FOLDER, GEOJSON_FILENAME)
with open(geojson_filepath, "w") as file:
    file.write(geojson_data)

print(f"GeoJSON data has been saved to {geojson_filepath}")
