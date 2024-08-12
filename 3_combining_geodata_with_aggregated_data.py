import geopandas as gpd
import pandas as pd
import json
from shapely.geometry import shape
import os

# Give the correct path to the data
MYDATAPATH = "dwd_weather_data"

# Load the aggregated data
with open(os.path.join(MYDATAPATH, "station_data_per_year.json"), "r") as f:
    json_objects = [json.loads(line) for line in f]

# Convert to DataFrame first
station_data_per_year = pd.DataFrame(json_objects)

# Convert the geometry from GeoJSON string to Shapely geometry object
station_data_per_year["geometry"] = station_data_per_year["geometry"].apply(
    lambda x: shape(json.loads(x))
)

# Now convert to GeoDataFrames
station_data_per_year = gpd.GeoDataFrame(station_data_per_year, geometry="geometry")

# Set the CRS to the original CRS of your data
# Replace 4326 with the correct EPSG code if it's different
station_data_per_year = station_data_per_year.set_crs(epsg=4326)

# If you need to transform to a different CRS (e.g., for Germany-specific analysis),
# you can do so after setting the correct original CRS:
station_data_per_year = station_data_per_year.to_crs(epsg=31467)

# Convert year to datetime and extract year
# station_data_per_year["year"] = pd.to_datetime(station_data_per_year["year"]).dt.year

# Sort the data
station_data_per_year = station_data_per_year.sort_values(["Stations_id", "year"])

print("Spatial data processing complete.")

# Save the processed data
output_filename = os.path.join(MYDATAPATH, "processed_station_data_per_year.geojson")
station_data_per_year.to_file(output_filename, driver="GeoJSON")

print(f"Data saved to {output_filename}")
