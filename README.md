# AI Nutritional Health Assistant — Personalized Guidance for Indian Diets

[![Python](https://img.shields.io/badge/python-3.x-blue)](https://www.python.org/)

A conversational AI nutrition assistant built for Indian diets. It uses **FastAPI**, **LangChain**, and a **RAG (Retrieval-Augmented Generation)** pipeline over **FAISS** to answer **100+ context-aware queries** across multiple Indian regional cuisines, aiming for ~90% accuracy in nutrition guidance.

**NEW**: Now with a modern **Next.js** frontend with TypeScript, React, and responsive design!

---

## 🚀 Features

* Personalized nutrition recommendations (calories, macros, micronutrients)
* Supports regional Indian cuisines (North, South, East, West)
* Conversational interface — e.g., "What should I eat for lunch in South India under 500 kcal?"
* Retrieval + LLM architecture: FAISS vector search with curated Indian food datasets
* Modern Next.js frontend with TypeScript and responsive design
* Modular and extensible — add new datasets, cuisines, or swap LLMs easily

---

## 📁 Project Structure

```plaintext
.
├── app/                      # FastAPI backend
│   ├── routers/              # API routes
│   ├── services/             # Business logic
│   ├── models.py             # Data models
│   └── main.py               # FastAPI app with CORS
├── frontend/                 # Next.js frontend (NEW!)
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   ├── lib/              # API client & utilities
│   │   └── styles/           # CSS modules
│   └── package.json
├── dockerfile                # Containerization
├── docker-compose.yml        # Orchestration
├── faiss_RAG.py              # RAG + FAISS pipeline
├── food_dataset.*            # Food/nutrition datasets
├── requirements.txt          # Python dependencies
├── start-servers.bat         # Launch both servers (Windows)
└── API_CONNECTION_SETUP.md   # API setup guide
```

---

## ⚙️ Setup & Installation

### Prerequisites

* Python 3.9+
* Node.js 18+ and npm
* PostgreSQL database
* (Optional) Docker & Docker Compose
* (Optional) GPU for faster inference

### Quick Start - Run Both Servers

**Windows Users**:
```bash
# Just double-click or run:
start-servers.bat
```

**Manual Setup**:

#### 1. Backend Setup (FastAPI)

```bash
# Clone and navigate to project
git clone https://github.com/theankitdash/AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets.git
cd AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload
```

Backend runs at: **http://localhost:8000**

#### 2. Frontend Setup (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Next.js dev server
npm run dev
```

Frontend runs at: **http://localhost:3000**

---

## 🌐 Using the Application

1. **Open your browser**: Navigate to `http://localhost:3000`

2. **Register/Login**: Create an account or login with existing credentials

3. **Set up your profile**:
   - Personal Details (height, weight, etc.)
   - Preferences (diet type, cuisines, activity level)
   - Health Conditions (allergies, medical conditions)

4. **Start chatting**: Ask nutrition questions in the chat interface!

---

## 🧠 API Endpoints

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
