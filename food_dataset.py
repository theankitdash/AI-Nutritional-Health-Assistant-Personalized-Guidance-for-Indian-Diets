import pandas as pd

# Load the dataset from the XLSX file
df = pd.read_excel("Food_dataset_Anuvaad.xlsx")

# Select only columns up to 'servings_unit'
df_up_to_servings_unit = df.loc[:, :'servings_unit']

# Save the resulting DataFrame to a CSV file
df_up_to_servings_unit.to_csv("food_dataset.csv", index=False)

print("File saved as 'output_file.csv'")