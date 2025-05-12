import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import json

# Step 1: Load Excel data
df = pd.read_csv("food_dataset.csv")

# Step 2: Convert rows to semantic descriptions
def row_to_text(row):
    return (
        f"{row['food_name']} ({row['servings_unit']}):\n"
        f"Food Code: {row['food_code']}, Primary Source: {row['primarysource']}\n"
        f"Energy: {row['energy_kcal']} kcal ({row['energy_kj']} kJ), Protein: {row['protein_g']} g, "
        f"Carbs: {row['carb_g']} g, Fat: {row['fat_g']} g, "
        f"Fibre: {row['fibre_g']} g, Sugar: {row['freesugar_g']} g, "
        f"Calcium: {row['calcium_mg']} mg, Iron: {row['iron_mg']} mg, Vitamin C: {row['vitc_mg']} mg\n"
        f"Cholesterol: {row['cholesterol_mg']} mg, Sodium: {row['sodium_mg']} mg, Potassium: {row['potassium_mg']} mg\n"
        f"Magnesium: {row['magnesium_mg']} mg, Phosphorus: {row['phosphorus_mg']} mg, Copper: {row['copper_mg']} mg\n"
        f"Selenium: {row['selenium_ug']} µg, Chromium: {row['chromium_mg']} mg, Manganese: {row['manganese_mg']} mg\n"
        f"Zinc: {row['zinc_mg']} mg, Vitamin A: {row['vita_ug']} µg, Vitamin E: {row['vite_mg']} mg, Vitamin D2: {row['vitd2_ug']} µg\n"
        f"Vitamin D3: {row['vitd3_ug']} µg, Vitamin K1: {row['vitk1_ug']} µg, Vitamin K2: {row['vitk2_ug']} µg\n"
        f"Folate: {row['folate_ug']} µg, Vitamin B1: {row['vitb1_mg']} mg, Vitamin B2: {row['vitb2_mg']} mg\n"
        f"Vitamin B3: {row['vitb3_mg']} mg, Vitamin B5: {row['vitb5_mg']} mg, Vitamin B6: {row['vitb6_mg']} mg\n"
        f"Vitamin B7: {row['vitb7_ug']} µg, Vitamin B9: {row['vitb9_ug']} µg, Carotenoids: {row['carotenoids_ug']} µg"
    )

texts = [row_to_text(row) for _, row in df.iterrows()]

print("Sample semantic descriptions:\n")
for i, text in enumerate(texts[:3], start=1):
    print(f"--- Entry {i} ---\n{text}\n")
    
# Step 3: Embed the texts
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

# Step 4: Index with FAISS
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# Save index and texts
faiss.write_index(index, "food_dataset/index.faiss")
with open("food_dataset/index.json", "w", encoding="utf-8") as f:
    json.dump(texts, f, ensure_ascii=False, indent=2)

print("FAISS index created and saved.")