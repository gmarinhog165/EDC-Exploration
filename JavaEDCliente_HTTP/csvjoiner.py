import pandas as pd

def merge_csvs(flow_csv_path, asset_csv_path, output_csv_path=None):
    # Load CSVs
    df_flows = pd.read_csv(flow_csv_path)
    df_assets = pd.read_csv(asset_csv_path)

    # Check for empty DataFrames
    if df_flows.empty:
        print("The flow CSV is empty (only headers or no data).")
        return
    if df_assets.empty:
        print("The asset CSV is empty (only headers or no data).")
        return

    # Merge on flow_id == TransferID
    merged_df = pd.merge(df_flows, df_assets, left_on='flow_id', right_on='TransferID', how='inner')

    if merged_df.empty:
        print("No matching rows found between flow_id and TransferID.")
    else:
        if output_csv_path:
            merged_df.to_csv(output_csv_path, index=False)
            print(f"Merged data saved to: {output_csv_path}")
        else:
            print("Merged Data:")
            print(merged_df)

# Example usage
merge_csvs( 'meucsv.csv','transfer_log.csv', 'merged_output.csv')
