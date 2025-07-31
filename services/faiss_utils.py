import os
from db_connect import connect_db
from langchain_huggingface import HuggingFaceEmbeddings
import faiss
import json
import numpy as np

# Build FAISS vectorstore manually — no pickle, no deserialization flag needed
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

os.makedirs("user_embeddings", exist_ok=True)

async def update_faiss_for_user(email: str):
    conn = await connect_db()
    
    # 1. Fetch combined data
    personal = await conn.fetchrow("SELECT * FROM personal_details WHERE email=$1", email)
    preferences = await conn.fetchrow("SELECT * FROM preferences WHERE email=$1", email)
    health = await conn.fetchrow("SELECT * FROM health_conditions WHERE email=$1", email)
    await conn.close()

    # 2. Convert to readable text
    user_profile_text = f"""
    Personal Info: {dict(personal)}
    Preferences: {dict(preferences)}
    Health Conditions: {dict(health)}
    """

    # Embed using HuggingFaceEmbeddings
    vector = embedding.embed_documents([user_profile_text])[0]
    vector = np.array(vector).astype("float32").reshape(1, -1)

    # Load or initialize FAISS index
    if os.path.exists("user_embeddings/index.faiss"):
        index = faiss.read_index("user_embeddings/index.faiss")
        with open("user_embeddings/index.json", "r", encoding="utf-8") as f:
            text_data = json.load(f)
    else:
        index = faiss.IndexFlatL2(vector.shape[1])
        text_data = []

    # If the user already exists, remove their old vector
    if any(email in t for t in text_data):
        idx = next(i for i, t in enumerate(text_data) if email in t)
        index.remove_ids(np.array([idx]))
        text_data.pop(idx)

    # Add new vector
    index.add(vector)
    text_data.append(user_profile_text)

    # Save everything
    faiss.write_index(index, "user_embeddings/index.faiss")
    with open("user_embeddings/index.json", "w", encoding="utf-8") as f:
        json.dump(text_data, f, ensure_ascii=False, indent=2)

    print(f"FAISS index updated for user: {email}")
