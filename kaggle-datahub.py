import kagglehub
import pandas as pd
import os

# Download latest version
path = kagglehub.dataset_download("utsavdey1410/food-nutrition-dataset")

print("Path to dataset files:", path)

# List of CSV file names
file_names = [
    "FOOD-DATA-GROUP1.csv",
    "FOOD-DATA-GROUP2.csv",
    "FOOD-DATA-GROUP3.csv",
    "FOOD-DATA-GROUP4.csv",
    "FOOD-DATA-GROUP5.csv"
]

# Load and concatenate all CSV files in one step
combined_data = pd.concat(
    [pd.read_csv(os.path.join(path, "FINAL FOOD DATASET", file)) for file in file_names],
    ignore_index=True
)

# Optionally refine the combined dataset
combined_data = combined_data.drop_duplicates()
combined_data = combined_data.dropna()

# Drop the first two columns
combined_data = combined_data.iloc[:, 2:]

# Save the refined combined data to a single CSV file in the current folder
combined_data.to_csv("Food_DATASET.csv", index=False)

print(f"Data Saved")