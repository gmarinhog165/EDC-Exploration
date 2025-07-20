import pandas as pd
import numpy as np
import os

def add_average_row_to_csv(file_path, columns_to_average):
    """
    Add an average row to a CSV file for specified columns.
    
    Args:
        file_path (str): Path to the CSV file
        columns_to_average (list): List of column names to calculate averages for
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Calculate averages for specified columns
        averages = {}
        for col in columns_to_average:
            if col in df.columns:
                averages[col] = df[col].mean()
            else:
                print(f"Warning: Column '{col}' not found in {file_path}")
        
        # Create a new row with averages
        new_row = {}
        for col in df.columns:
            if col in averages:
                new_row[col] = averages[col]
            else:
                # For non-numeric columns, use "AVERAGE" as identifier
                if col == df.columns[0]:  # First column (ID column)
                    new_row[col] = "AVERAGE"
                else:
                    new_row[col] = ""
        
        # Add the new row to the dataframe
        df_with_avg = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Save back to the same file
        df_with_avg.to_csv(file_path, index=False)
        
        print(f"Added average row to {file_path}")
        for col, avg in averages.items():
            print(f"  {col}: {avg:.3f}")
        print()
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def main():
    # Define the files and their respective columns to average
    files_config = {
        'dataflow_timing.csv': [
            'received_to_started_seconds',
            'started_to_completed_seconds', 
            'total_duration_seconds'
        ],
        'edc_enhanced_timing.csv': [
            'contract_signature_time_seconds',
            'policy_verification_time_seconds'
        ]
    }
    
    # Process each file
    for file_path, columns in files_config.items():
        if os.path.exists(file_path):
            add_average_row_to_csv(file_path, columns)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
