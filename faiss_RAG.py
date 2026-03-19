import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import json

# Step 1: Load CSV data
df = pd.read_csv("food_dataset.csv")

# Step 2: Convert rows to semantic descriptions (shorter, embedding-friendly)
def row_to_text(row):
    return (
        f"{row['food_name']} ({row['servings_unit']}):\n"
        f"Primary Source: {row['primarysource']}\n"
        f"Energy: {row['energy_kcal']} kcal, Protein: {row['protein_g']} g, "
        f"Carbs: {row['carb_g']} g, Fat: {row['fat_g']} g, "
        f"Fibre: {row['fibre_g']} g, Sugar: {row['freesugar_g']} g\n"
        f"Calcium: {row['calcium_mg']} mg, Iron: {row['iron_mg']} mg, "
        f"Vitamin C: {row['vitc_mg']} mg, Sodium: {row['sodium_mg']} mg, "
        f"Potassium: {row['potassium_mg']} mg, Cholesterol: {row['cholesterol_mg']} mg"
    )


# Step 3: Extract structured metadata per row
def row_to_metadata(row):
    return {
        "food_name": str(row.get("food_name", "")),
        "food_code": str(row.get("food_code", "")),
        "primarysource": str(row.get("primarysource", "")),
        "servings_unit": str(row.get("servings_unit", "")),
        "energy_kcal": float(row.get("energy_kcal", 0)),
        "protein_g": float(row.get("protein_g", 0)),
        "carb_g": float(row.get("carb_g", 0)),
        "fat_g": float(row.get("fat_g", 0)),
        "fibre_g": float(row.get("fibre_g", 0)),
        "freesugar_g": float(row.get("freesugar_g", 0)),
        "calcium_mg": float(row.get("calcium_mg", 0)),
        "iron_mg": float(row.get("iron_mg", 0)),
        "vitc_mg": float(row.get("vitc_mg", 0)),
        "cholesterol_mg": float(row.get("cholesterol_mg", 0)),
        "sodium_mg": float(row.get("sodium_mg", 0)),
        "potassium_mg": float(row.get("potassium_mg", 0)),
    }


texts = [row_to_text(row) for _, row in df.iterrows()]
metadata = [row_to_metadata(row) for _, row in df.iterrows()]

print("Sample semantic descriptions:\n")
for i, text in enumerate(texts[:3], start=1):
    print(f"--- Entry {i} ---\n{text}\n")

# Step 4: Embed the texts
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

# Step 5: Index with FAISS
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# Step 6: Save FAISS index and texts
faiss.write_index(index, "app/food_dataset/index.faiss")
with open("app/food_dataset/index.json", "w", encoding="utf-8") as f:
    json.dump(texts, f, ensure_ascii=False, indent=2)

# Step 7: Save metadata
with open("app/food_dataset/metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

# Step 8: Save tokenized BM25 corpus
bm25_corpus = [text.lower().split() for text in texts]
with open("app/food_dataset/bm25_corpus.json", "w", encoding="utf-8") as f:
    json.dump(bm25_corpus, f, ensure_ascii=False)

print("FAISS index, metadata, and BM25 corpus created and saved.")