import pandas as pd
from difflib import SequenceMatcher
from collections import defaultdict
import warnings
import argparse

# Suppress warnings
warnings.filterwarnings('ignore')

def similar(a, b):
    """Compute similarity ratio between two strings."""
    return SequenceMatcher(None, a, b).ratio()

def load_reference_csv(filepath):
    """Load reference CSV and get the column names."""
    df = pd.read_csv(filepath)
    columns = df.columns.tolist()
    return columns

def clean_csv(df, ref_columns):
    """Clean a dataframe based on reference columns."""
    
    # Add an "END DATE" column with values identical to the "Date" column (if it exists)
    if 'Date' in df.columns:
        df['END DATE'] = df['Date']

    # Identify groups of similar columns based on string similarity
    column_names = df.columns.tolist()
    similar_column_groups = defaultdict(list)
    grouped_columns = set()

    for i, col1 in enumerate(column_names):
        if col1 not in grouped_columns:
            for j, col2 in enumerate(column_names):
                if i != j and col2 not in grouped_columns and similar(col1.lower(), col2.lower()) > 0.75:
                    similar_column_groups[col1].append(col2)
                    grouped_columns.add(col2)
            grouped_columns.add(col1)

    # Consolidate the data from similar columns into a single column
    consolidated_data = df.copy()
    for group, similar_cols in similar_column_groups.items():
        consolidated_data[group] = df[similar_cols + [group]].bfill(axis=1).iloc[:, 0]

    # Remove the original similar columns to avoid duplication
    for similar_cols in similar_column_groups.values():
        consolidated_data.drop(columns=similar_cols, inplace=True, errors='ignore')
    
    # Keep only the columns that are present in the reference CSV
    final_data = consolidated_data[consolidated_data.columns.intersection(ref_columns)]

    return final_data

def main():
    parser = argparse.ArgumentParser(description="Clean CSV files based on a reference CSV.")
    parser.add_argument("input_csv", help="Path to the input CSV file to be cleaned.")
    parser.add_argument("reference_csv", help="Path to the reference CSV file.")
    parser.add_argument("output_csv", help="Path to save the cleaned CSV file.")
    
    args = parser.parse_args()

    # Load reference CSV columns
    ref_columns = load_reference_csv(args.reference_csv)
    
    # Load and clean the input CSV
    df = pd.read_csv(args.input_csv)
    cleaned_data = clean_csv(df, ref_columns)
    
    # Save the cleaned data to the specified output path
    cleaned_data.to_csv(args.output_csv, index=False)

# This ensures the script only runs when executed directly (and not when imported as a module)
if __name__ == "__main__":
    main()
