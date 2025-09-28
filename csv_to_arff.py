import pandas as pd
import numpy as np
import argparse
import os

def infer_attribute_type(series):
    """
    Infer the ARFF attribute type from a pandas Series.
    
    Args:
        series: pandas Series to analyze
    
    Returns:
        str: ARFF attribute type declaration
    """
    # Remove NaN values for type inference
    non_null_series = series.dropna()
    
    if len(non_null_series) == 0:
        return "STRING"
    
    # Check if it's boolean first (before numeric check)
    if pd.api.types.is_bool_dtype(series):
        return "{True,False}"
    
    # Check for boolean-like values (True/False as strings or mixed)
    unique_values = set(str(val).upper() for val in non_null_series.unique())
    if unique_values.issubset({'TRUE', 'FALSE'}):
        return "{True,False}"
    
    # Check if it's numeric
    if pd.api.types.is_numeric_dtype(series):
        if pd.api.types.is_integer_dtype(series):
            return "INTEGER"
        else:
            return "REAL"
    
    # Check if it's a categorical with few unique values
    unique_values = non_null_series.unique()
    if len(unique_values) <= 20:  # Threshold for categorical
        # Create nominal attribute with all possible values, replace spaces with underscores
        unique_str = []
        for val in sorted(unique_values):
            if isinstance(val, str):
                cleaned_val = str(val).replace(' ', '_')
                unique_str.append(cleaned_val)
            else:
                unique_str.append(str(val))
        return "{" + ",".join(unique_str) + "}"
    
    # Default to STRING for everything else
    return "STRING"

def csv_to_arff(csv_file, arff_file=None, relation_name=None):
    """
    Convert a CSV file to ARFF format.
    
    Args:
        csv_file: Path to input CSV file
        arff_file: Path to output ARFF file (optional)
        relation_name: Name for the relation (optional)
    """
    # Read CSV file
    try:
        df = pd.read_csv(csv_file)
        print(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Generate output filename if not provided
    if arff_file is None:
        base_name = os.path.splitext(csv_file)[0]
        arff_file = base_name + ".arff"
    
    # Generate relation name if not provided
    if relation_name is None:
        relation_name = os.path.splitext(os.path.basename(csv_file))[0]
    
    # Start writing ARFF file
    try:
        with open(arff_file, 'w') as f:
            # Write header
            f.write(f"@RELATION {relation_name}\n\n")
            
            # Write attribute declarations
            for column in df.columns:
                attr_type = infer_attribute_type(df[column])
                f.write(f"@ATTRIBUTE {column} {attr_type}\n")
            
            # Write data section
            f.write("\n@DATA\n")
            
            # Write data rows
            for _, row in df.iterrows():
                # Convert values to strings, handling NaN
                values = []
                for val in row:
                    if pd.isna(val):
                        values.append("?")  # ARFF missing value indicator
                    elif isinstance(val, str):
                        # Replace spaces with underscores but keep quotes
                        cleaned_val = val.replace(' ', '_')
                        # Escape commas and quotes in strings for ARFF format
                        if ',' in cleaned_val or '"' in cleaned_val:
                            escaped_val = cleaned_val.replace('"', '\\"')
                            values.append(f'"{escaped_val}"')
                        else:
                            values.append(cleaned_val)
                    else:
                        values.append(str(val))
                
                f.write(",".join(values) + "\n")
        
        print(f"Successfully converted {csv_file} to {arff_file}")
        print(f"Relation name: {relation_name}")
        
    except Exception as e:
        print(f"Error writing ARFF file: {e}")

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Convert CSV files to ARFF format")
    parser.add_argument("csv_file", help="Input CSV file path")
    parser.add_argument("-o", "--output", help="Output ARFF file path")
    parser.add_argument("-r", "--relation", help="Relation name for ARFF file")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.csv_file):
        print(f"Error: Input file '{args.csv_file}' does not exist")
        return
    
    # Convert CSV to ARFF
    csv_to_arff(args.csv_file, args.output, args.relation)

if __name__ == "__main__":
    # If run without command line arguments, convert test.csv as example
    import sys
    if len(sys.argv) == 1:
        print("No arguments provided. Converting test.csv as example...")
        csv_to_arff("test.csv", relation_name="test_data")
    else:
        main()
