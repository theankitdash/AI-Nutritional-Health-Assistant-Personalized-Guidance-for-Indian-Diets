# AI Nutritional Health Assistant — Personalized Guidance for Indian Diets

[![Python](https://img.shields.io/badge/python-3.x-blue)](https://www.python.org/)

A conversational AI nutrition assistant built for Indian diets. It uses **FastAPI**, **LangChain**, and a **RAG (Retrieval-Augmented Generation)** pipeline over **FAISS** to answer **100+ context-aware queries** across multiple Indian regional cuisines, aiming for ~90% accuracy in nutrition guidance.

---

## 🚀 Features

* Personalized nutrition recommendations (calories, macros, micronutrients)
* Supports regional Indian cuisines (North, South, East, West)
* Conversational interface — e.g., “What should I eat for lunch in South India under 500 kcal?”
* Retrieval + LLM architecture: FAISS vector search with curated Indian food datasets
* Modular and extensible — add new datasets, cuisines, or swap LLMs easily

---

## 📁 Project Structure

```plaintext
.
├── app/                      # FastAPI app, routers, models, etc.
├── dockerfile                # Containerization
├── docker-compose.yml        # Orchestration (API/DB etc.)
├── faiss_RAG.py              # RAG + FAISS pipeline
├── food_dataset.*            # Food/nutrition dataset files
├── usda-food.py              # USDA-based mapping utility
├── requirements.txt          # Python dependencies
└── .gitignore
```

---

## ⚙️ Setup & Installation

### Prerequisites

* Python 3.9+
* (Optional) Docker & Docker Compose
* (Optional) GPU for faster inference

### Local Setup

1. Clone the repository:
   `git clone https://github.com/theankitdash/AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets.git`
   `cd AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets`

2. Create and activate a virtual environment:
   `python3 -m venv venv`
   `source venv/bin/activate` (Windows: `venv\Scripts\activate`)

3. Install dependencies:
   `pip install -r requirements.txt`

4. Start the FastAPI app:
   `uvicorn app.main:app --reload`

Open [http://localhost:8000](http://localhost:8000) to access the API.

### Docker Setup (Optional)

`docker-compose up --build`

This will start the API (and other services if configured) in containers.

---

## 🧠 Usage Examples / API Endpoints

**Example Endpoints:**

* `POST /api/v1/nutrition/query` — Ask personalized meal suggestions.
* `GET /api/v1/health/status` — Health check.
* `GET /api/v1/food/{food_id}` — Fetch nutritional info for a specific item.

**Example Request:**

```json
{
  "age": 28,
  "gender": "male",
  "region": "south",
  "height_cm": 170,
  "weight_kg": 70,
  "goal": "maintain",
  "diet_preferences": ["vegetarian"],
  "query": "What can I eat for dinner under 400 kcal in Tamil Nadu?"
}
```

**Example Response:**

```json
{
  "calorie_target": 2000,
  "recommended_meals": [
    {
      "meal": "Dinner",
      "items": ["Ragi dosa", "Sambar", "Cucumber salad"],
      "nutrients": {
        "calories": 380,
        "protein_g": 12,
        "carbs_g": 60,
        "fat_g": 6
      }
    }
  ],
  "notes": "This is approximate. Adjust based on personal preferences."
}
```

---

## 🧩 Architecture

* **RAG pipeline**: FAISS vector search over curated food/nutrition data
* **LLM prompt augmentation**: Retrieved context guides AI responses
* **Regional diet adaptation**: Dataset tagging and filtering for Indian cuisines
* **Extensible components**: Swap embeddings, LLM models, or vector stores easily

---

## ✅ Limitations & Future Work

* Accuracy depends on dataset quality; edge cases may deviate
* Not intended for medical or clinical nutrition advice
* Expand to more regional cuisines (e.g., Assamese, Goan, Kashmiri)
* Include detailed micronutrients, portion sizes, and allergy checks
* Implement user feedback loop for continuous improvement

---

## 🛠️ Contributing

1. Fork the repository
2. Create a feature branch
3. Commit with clear messages
4. Submit a pull request

We welcome dataset improvements, bug fixes, and new regional cuisines.

---

## 📜 License
Check dataset licenses (e.g., USDA, Indian food tables) for usage compliance.

---

## 🎯 Quick Start Tips

* Start small: test one region with a small dataset.
* Log prompts/responses for debugging retrieval + LLM alignment.
* Add fallback rules for edge-case queries.
* Build a feedback loop for refining suggestions over time.
