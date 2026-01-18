# 🥗 AI Nutritional Health Assistant — Personalized Guidance for Indian Diets

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.125.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

A conversational AI nutrition assistant specializing in Indian diets. Built with **FastAPI**, **LangGraph**, and a **RAG (Retrieval-Augmented Generation)** pipeline powered by **FAISS** vector search. Delivers context-aware nutrition guidance across multiple Indian regional cuisines with a modern **Next.js + TypeScript** frontend.

---

## ✨ Key Features

- 🍛 **Regional Indian Cuisine Support** — North, South, East, and West Indian cuisines
- 🤖 **AI-Powered Recommendations** — Personalized meal suggestions using RAG + LLM
- 💬 **Conversational Interface** — Natural language queries like "What should I eat for lunch in South India under 500 kcal?"
- 📊 **Comprehensive Nutrition Data** — Calories, macros (protein, carbs, fat), and micronutrients
- 🎯 **Goal-Based Planning** — Weight loss, maintenance, or muscle gain
- 🌱 **Dietary Preferences** — Vegan, vegetarian, non-vegetarian options
- 🏥 **Health Condition Awareness** — Allergy tracking and medical condition considerations
- 📱 **Modern Web Interface** — Responsive Next.js frontend with TypeScript
- 🐳 **Docker Support** — Easy deployment with Docker Compose
- 🔒 **User Authentication** — Secure login and profile management

---

## 🏗️ Architecture

### Tech Stack

#### Backend
- **FastAPI** — High-performance async Python web framework
- **LangGraph** — Advanced workflow orchestration for AI agents
- **LangChain** — LLM application framework
- **FAISS** — Vector similarity search for RAG pipeline
- **Sentence Transformers** — Text embeddings (HuggingFace)
- **PostgreSQL** — User data and profile storage
- **SQLAlchemy** — ORM for database operations
- **Pydantic** — Data validation and settings management

#### Frontend
- **Next.js 14** — React framework with App Router
- **TypeScript** — Type-safe JavaScript
- **React 18** — Modern UI library

#### Infrastructure
- **Docker & Docker Compose** — Containerization
- **Uvicorn** — ASGI server
- **NVIDIA AI Endpoints** — LLM inference (optional)

### System Design

```
┌─────────────┐          ┌──────────────┐          ┌─────────────┐
│   Next.js   │  HTTP    │   FastAPI    │  Vector  │    FAISS    │
│  Frontend   │─────────▶│   Backend    │  Search  │   Index     │
│             │          │              │─────────▶│             │
└─────────────┘          └──────────────┘          └─────────────┘
                                │
                                │ SQL
                                ▼
                         ┌──────────────┐
                         │  PostgreSQL  │
                         │   Database   │
                         └──────────────┘
```

**RAG Pipeline Flow:**
1. User query → Embedding generation
2. FAISS vector search → Retrieve relevant food data
3. Context + Query → LLM prompt augmentation
4. LLM generates personalized nutrition advice
5. Response returned to user

---

## 📁 Project Structure

```plaintext
.
├── app/                        # FastAPI Backend
│   ├── routers/                # API route handlers
│   ├── services/               # Business logic layer
│   ├── models.py               # SQLAlchemy database models
│   ├── database.py             # Database configuration
│   └── main.py                 # FastAPI application entry point
│
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/                # Next.js App Router pages
│   │   ├── components/         # Reusable React components
│   │   ├── lib/                # API client & utilities
│   │   └── styles/             # Global styles
│   └── package.json            # Node.js dependencies
│
├── faiss_RAG.py                # RAG pipeline implementation
├── food_dataset.csv            # Curated Indian food nutrition data
├── food_dataset.json           # JSON format food data
├── Food_dataset_Anuvaad.xlsx   # Regional dataset
├── requirements.txt            # Python dependencies
├── dockerfile                  # Docker image definition
├── docker-compose.yml          # Multi-container orchestration
├── start-servers.bat           # Quick start script (Windows)
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** (3.10 or 3.11 recommended)
- **Node.js 22+** and npm
- **PostgreSQL 17** 
- **Git**

### Quick Start with Docker 🐳 (Recommended)

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/theankitdash/AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets.git
cd AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets

# Backend will be at: http://localhost:8000
# Database will be at: localhost:5432
```

Then **manually start the frontend** (not in Docker yet):

```bash
cd frontend
npm install
npm run dev
# Frontend will be at: http://localhost:3000
```

### Manual Setup (Without Docker)

#### 1. Backend Setup

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at: **http://localhost:8000**  

#### 2. Frontend Setup

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install Node.js dependencies
npm install

# Start Next.js development server
npm run dev
```

✅ Frontend running at: **http://localhost:3000**

#### 3. Database Setup
- Download and install from [postgresql.org](https://www.postgresql.org/download/)
- Create database: `createdb nutrify_db`

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

## 🌐 Using the Application

### 1. **Access the Application**
Navigate to `http://localhost:3000` in your browser

### 2. **Register/Login**
- Create a new account with email and password
- Or login with existing credentials

### 3. **Complete Your Profile**

Set up three key sections:

- **Personal Details**
  - Age, gender, height, weight
  - Activity level (sedentary, moderate, active)

- **Dietary Preferences**
  - Diet type (vegan, vegetarian, non-veg)
  - Regional cuisines
  - Meal preferences

- **Health Conditions**
  - Allergies (nuts, dairy, etc.)
  - Medical conditions (diabetes, hypertension, etc.)
  - Dietary restrictions

### 4. **Start Chatting!**

Ask questions like:
- *"What should I eat for lunch in South India under 500 kcal?"*
- *"Give me a high-protein vegetarian dinner option"*
- *"I need a meal plan for weight loss with North Indian food"*
- *"What's a healthy breakfast option with less than 300 calories?"*

---

## 📊 Dataset Information

The application uses curated Indian food nutrition datasets:

- **food_dataset.csv** — Primary nutrition database with Indian foods
- **Food_dataset_Anuvaad.xlsx** — Regional cuisine data
- **Sources**: USDA FoodData Central, Indian Food Composition Tables

---

## ⚠️ Important Notes & Limitations

> [!WARNING]
> **Medical Disclaimer**: This application is for informational purposes only and is NOT intended as medical or clinical nutrition advice. Always consult healthcare professionals for medical nutrition therapy.

- **Accuracy**: Nutrition data accuracy depends on dataset quality; edge cases may vary
- **Regional Coverage**: Currently focused on major Indian regions; some cuisines may have limited data
- **Allergies**: Always double-check ingredients if you have severe allergies
- **Portion Sizes**: Estimates are approximate; actual portions may vary
- **GPU**: Embeddings are faster with GPU, but CPU works fine for moderate use

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

1. **Dataset Improvements**
   - Add more regional Indian foods
   - Improve nutrition data accuracy
   - Add recipe information

2. **Code Contributions**
   - Bug fixes
   - New features (see Roadmap)
   - Performance optimizations
   - Test coverage

3. **Documentation**
   - Fix typos or improve clarity
   - Add examples
   - Translate to other languages

### Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with clear, descriptive commits
4. Add tests if applicable
5. Update documentation
6. Submit a Pull Request

Please follow coding standards and include tests for new features.

---

### Dataset Licenses
- USDA FoodData Central: Public Domain
- Indian Food Composition Tables: Check specific source licenses

---

Made with ❤️ for healthier Indian diets
