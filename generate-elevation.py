'''
GETTING ELEVATION

Getting elevation involved two steps:

1. Getting elevation data in bulk, with cooresponding longitude and latitude, 
and saving them to elevation_data.csv file.

2. Assigning an elevation for every entry using the elevation-data.csv

For step 1, we are using https://api.opentopodata.org/v1/aster30m. To reduce
API usage and to prevent hitting the API limit, we need to bulk get elevation
data for 100 locations at once for every request.

The returned request will be essentially a list of dictionaries, each dictionary
containing information on longitude, latitude, and elevation at that point.

We cannot then use this data and immediately add values to our tsunami runups data.
This is because
1. The returned elevations are not in the same order as we had requested them.
   We request elevation for locations A, B, C, but the API may return it as
   B, C, A
2. The API does not have as high as a precision as our tsunami runups dataset.
   We requested location (1.234567, 8.912345) but the API only returns (1.23, 8.91)
2. Some locations are unavailable, they return null for elevation

So, we store the longitude and latitude and corresponding elevation in a separate
CSV file, in elevation_data.csv.

Then, we loop over the tsunami runups data again, and apply the elevation using
the closest longitude and latitude available in elevation_data.csv.

Creating elevation_data.csv is done here

Applying elevation_data.csv is done in apply_elevation.py
'''

import pandas as pd
import requests
from time import sleep

INPUT_CSV = 'tsunami_runups.csv'
OUTPUT_CSV = 'elevation_data.csv'

all_elevation = {}

def bulk_get_elevation(locations: list[tuple[float, float]]):
    global all_elevation

    """
    Get elevation data for a list of (latitude, longitude) tuples.
    
    Args:
        locations: List of (lat, lon) tuples
    
    Returns:
        str: Pipe-separated string format "lat1,lon1|lat2,lon2|..."
    """ 
    if not locations:
        return ""
    
    # Convert list of tuples to pipe-separated string format
    coordinate_strings = []
    for lat, lon in locations:
        coordinate_strings.append(f"{lat},{lon}")
    
    request_url = "https://api.opentopodata.org/v1/aster30m?interpolation=nearest&locations=" + "|".join(coordinate_strings)
    
    try:
        response = requests.get(request_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        json_data = response.json()

        for result in json_data.get("results", []):
            loc = (float(result.get("location", {})["lat"]), float(result.get("location", {})["lng"]))
            elevation = result.get("elevation", None)
            
            all_elevation[loc] = elevation

        sleep(3)
            
        return json_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

        quit()
        return None

def process_tsunami_coordinates():

    """
    Load tsunami CSV data and process latitude/longitude coordinates.
    For every 100 coordinate pairs, add a TODO and clear the list.
    """
    # Load the CSV file
    csv_file = INPUT_CSV
    df = pd.read_csv(csv_file)
    
    print(f"Loaded {len(df)} rows from {csv_file}")
    
    # Initialize list to store coordinate pairs
    coordinate_list = []
    entry_counts = 0
    
    # Process each row
    for idx, (_, row) in enumerate(df.iterrows()):
        # Get latitude and longitude values
        lat = float(row['latitude'])
        lon = float(row['longitude'])
        
        # Add coordinate pair to list
        coordinate_list.append((lat, lon))
        
        # Check if list has reached 100 items
        if len(coordinate_list) == 100:
            entry_counts += 1
            start_row = idx - 99
            
            bulk_get_elevation(coordinate_list)

            # Clear the list
            coordinate_list = []

            # Write all_elevation to CSV file
            elevation_df = pd.DataFrame([
                {'latitude': lat, 'longitude': lon, 'elevation': elevation}
                for (lat, lon), elevation in all_elevation.items()
            ])
            elevation_df.to_csv(OUTPUT_CSV, index=False)
            print(f"Wrote running elevation records. Current length is {len(all_elevation)}")
    
    # Handle any remaining coordinates
    if coordinate_list:
        bulk_get_elevation(coordinate_list)

        elevation_df = pd.DataFrame([
                {'latitude': lat, 'longitude': lon, 'elevation': elevation}
                for (lat, lon), elevation in all_elevation.items()
            ])

    print(f"\nProcessing complete! Created {entry_counts + (1 if coordinate_list else 0)} items")

if __name__ == "__main__":
    process_tsunami_coordinates()
