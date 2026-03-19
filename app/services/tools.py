from app.services.hybrid_retriever import hybrid_search

def search_food_database(query: str, k: int = 5) -> str:
    
    docs = hybrid_search(query, k_final=k)
    if not docs:
        return "No relevant food items found in the database."

    results = []
    for i, doc in enumerate(docs, 1):
        food_name = doc.metadata.get("food_name", "Unknown")
        energy = doc.metadata.get("energy_kcal", "N/A")
        protein = doc.metadata.get("protein_g", "N/A")
        carbs = doc.metadata.get("carb_g", "N/A")
        fat = doc.metadata.get("fat_g", "N/A")

        results.append(
            f"{i}. **{food_name}** — {energy} kcal | "
            f"P: {protein}g | C: {carbs}g | F: {fat}g\n"
            f"   {doc.page_content}"
        )
    return "\n\n".join(results)


def get_nutrition_facts(food_name: str) -> str:
   
    docs = hybrid_search(food_name, k_final=3)
    if not docs:
        return f"No nutrition data found for '{food_name}'."

    # Return the top match with full details
    top = docs[0]
    return top.page_content
