import pandas as pd
import math

def find_closest_elevation(target_lat, target_lon, elevation_dict):
    """
    Find the closest elevation data for given coordinates using Euclidean distance.
    
    Args:
        target_lat: Target latitude
        target_lon: Target longitude
        elevation_dict: Dictionary mapping (lat, lon) tuples to elevation values
    
    Returns:
        tuple: (elevation value, distance) of the closest coordinate, or (None, None) if no data available
    """
    if not elevation_dict:
        return None, None
    
    closest_key = None
    min_distance = float('inf')
    
    for (lat, lon) in elevation_dict.keys():
        # Calculate Euclidean distance
        distance = math.sqrt((target_lat - lat) ** 2 + (target_lon - lon) ** 2)
        
        if distance < min_distance:
            min_distance = distance
            closest_key = (lat, lon)
    
    if closest_key:
        return elevation_dict[closest_key], min_distance
    else:
        return None, None

def apply_elevation_data():
    """
    Apply elevation data to tsunami CSV by finding nearest coordinates.
    """
    # 1. Load tsunami CSV
    print("Loading tsunami data...")
    tsunami_file = 'output_tsunami_logtransformed_discretized_droppednoneq_addedepmag_dropleakage&ids_dropextmissing_repmissing.csv'
    tsunami_df = pd.read_csv(tsunami_file)
    print(f"Loaded {len(tsunami_df)} tsunami records")
    
    # 2. Load elevation data CSV
    print("Loading elevation data...")
    elevation_df = pd.read_csv('elevation_data.csv')
    print(f"Loaded {len(elevation_df)} elevation records")
    
    # Convert elevation data to dictionary for faster lookup
    elevation_dict = {}
    for _, row in elevation_df.iterrows():
        elevation_dict[(row['latitude'], row['longitude'])] = row['elevation']
    
    # 3. For every entry in tsunami CSV, find nearest elevation
    print("Applying elevation data to tsunami records...")
    elevations = []
    distances = []
    
    for count, (idx, row) in enumerate(tsunami_df.iterrows()):
        if count % 1000 == 0:  # Progress indicator
            print(f"Processing row {count}/{len(tsunami_df)}")
        
        target_lat = float(row['latitude'])
        target_lon = float(row['longitude'])
        
        # Find closest elevation and distance
        elevation, distance = find_closest_elevation(target_lat, target_lon, elevation_dict)
        elevations.append(elevation)
        distances.append(distance)
    
    # Add elevation and distance columns to tsunami dataframe
    tsunami_df['elevation'] = elevations
    tsunami_df['elevation_distance'] = distances
    
    # 4. Write out new CSV with elevation data added
    output_file = 'tsunami_with_elevation.csv'
    tsunami_df.to_csv(output_file, index=False)
    print(f"Wrote {len(tsunami_df)} records with elevation data to {output_file}")
    
    # Print some statistics
    non_null_elevations = sum(1 for e in elevations if e is not None)
    print(f"Successfully matched elevation data for {non_null_elevations}/{len(elevations)} records")
    
    # Print distance statistics
    valid_distances = [d for d in distances if d is not None]
    if valid_distances:
        avg_distance = sum(valid_distances) / len(valid_distances)
        min_distance = min(valid_distances)
        max_distance = max(valid_distances)
        print(f"Distance statistics - Min: {min_distance:.6f}, Max: {max_distance:.6f}, Average: {avg_distance:.6f}")

if __name__ == "__main__":
    apply_elevation_data()