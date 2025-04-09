import pandas as pd

df = pd.read_excel('Food_dataset_Anuvaad.xlsx')  # Load the dataset into a pandas dataframe

# Convert to JSON
json_data = df.to_json(orient="records", indent=4)

# Save to a JSON file
with open("food_dataset.json", "w") as json_file:
    json_file.write(json_data)

print("Excel data successfully converted to JSON!")