# 🥗 AI Nutritional Health Assistant — Personalized Guidance for Indian Diets

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.1.6-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

A conversational AI nutrition assistant specializing in Indian diets. Built with **FastAPI**, **LangGraph**, and a **RAG (Retrieval-Augmented Generation)** pipeline powered by **FAISS** vector search. Delivers context-aware nutrition guidance across multiple Indian regional cuisines with a modern **Next.js 16 + TypeScript** frontend and **PostgreSQL** database backend.

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
- **asyncpg** — Async PostgreSQL adapter
- **Pydantic** — Data validation and settings management

#### Frontend
- **Next.js 16** — React framework with App Router
- **React 18** — Modern UI library
- **TypeScript 5.0+** — Type-safe JavaScript

#### Infrastructure
- **Docker & Docker Compose** — Containerization with multi-container orchestration
- **PostgreSQL 17** — Containerized database service
- **Uvicorn** — ASGI server for FastAPI
- **NVIDIA API Endpoints** — LLM inference (optional)

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
- **PostgreSQL 17** (or Docker for containerized deployment)
- **Git**
- **.env file** with database and API credentials (see Configuration section)

For **Docker deployment**: Only need **Docker** and **Docker Compose**

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/theankitdash/AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets.git
cd AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets

# Create .env file with database credentials
cp .env.example .env  # (or create manually with required variables)

# Start all services with Docker Compose
docker-compose up --build
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

### Manual Setup (Without Docker)

#### Prerequisites
- Python 3.9+
- PostgreSQL 17 (must be running before starting backend)
- Node.js 22+

#### 1. Backend Setup

```bash
# Navigate to project root
cd AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets

# Install Python dependencies
pip install -r app/requirements.txt

# Create and configure .env file (see Configuration section below)

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at: **http://localhost:8000**  
📚 API Documentation: **http://localhost:8000/docs**

#### 2. Frontend Setup (in new terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start Next.js development server
npm run dev
```

✅ Frontend running at: **http://localhost:3000**

#### 3. Database Setup

PostgreSQL must be running before starting the backend:

```bash
# On Windows (if PostgreSQL installed locally):
# PostgreSQL service should auto-start or start from Services

# On macOS/Linux:
brew services start postgresql
# or
sudo systemctl start postgresql

# Create database (optional, can be auto-created):
createdb nutrify_db
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DB_NAME=nutrify_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost          # Use 'postgres-db' for Docker
DB_PORT=5432

# API Configuration
API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000  # For Docker: http://fastapi:8000

# LLM Configuration (Optional - for NVIDIA API integration)
NVIDIA_API_KEY=your_nvidia_api_key
```

### Docker Environment

When using Docker Compose, update the `.env` file to use Docker service names:

```env
# For Docker services, use service names instead of localhost
DB_HOST=postgres-db
NEXT_PUBLIC_API_URL=http://fastapi:8000
```

## 🌐 Using the Application

### 1. **Access the Application**
Navigate to `http://localhost:3000` in your browser

### 2. **Register/Login**
- Create a new account with email and password
- Or login with existing credentials
- Password is securely hashed with bcrypt

### 3. **Complete Your Profile**

Set up three key sections after logging in:

#### Personal Details
- Age/Date of Birth, gender, height, weight
- Waist circumference
- Activity level (sedentary, moderate, active)

#### Dietary Preferences  
- Diet type (vegan, vegetarian, non-vegetarian)
- Regional cuisines (North, South, East, West Indian)
- Preferred meal types and ingredients
- Snack and sweet preferences
- Spice tolerance
- Caffeine intake
- Hydration level
- Meal frequency and eating out frequency

#### Health Conditions
- Food allergies and restrictions
- Medical conditions (diabetes, hypertension, etc.)
- Sleep quality and duration
- Supplement usage
- Fitness goals (weight loss, maintenance, muscle gain)

### 4. **Start Chatting!**

Ask the AI assistant questions like:
- *"What should I eat for lunch in South India under 500 kcal?"*
- *"Give me a high-protein vegetarian dinner option"*
- *"I need a meal plan for weight loss with North Indian food"*
- *"What's a healthy breakfast option with less than 300 calories?"*
- *"Suggest meals for someone with dairy allergies"*
- *"I'm diabetic, what are safe Indian meal options?"*

The assistant will provide personalized recommendations based on:
- Your dietary preferences
- Health conditions and allergies
- Fitness goals
- Regional cuisine preferences
- Nutritional requirements

---

## 📊 Dataset Information

The application uses curated Indian food nutrition datasets:

**Data Files**:
- `food_dataset.csv` — Primary nutrition database with Indian foods
- `food_dataset.json` — JSON format of food data
- `Food_dataset_Anuvaad.xlsx` — Extended regional cuisine data with translations

**Data Attributes**:
- Food name and aliases
- Calories and macronutrients (protein, carbohydrates, fat)
- Micronutrients (vitamins, minerals)
- Regional origin and cuisine type
- Common preparation methods

**Data Sources**: 
- USDA FoodData Central
- Indian Food Composition Tables (IFCT)
- Regional Indian nutrition studies

**FAISS Indexing**:
- Food data is embedded using Sentence Transformers
- FAISS index stored in `app/food_dataset/`
- Enables fast semantic search for food recommendations

---

## ⚠️ Important Notes & Limitations

> [!WARNING]
> **Medical Disclaimer**: This application is for informational and educational purposes only and is NOT intended as medical or clinical nutrition advice. Always consult licensed healthcare professionals (doctors, registered dietitians) for:
> - Medical nutrition therapy
> - Chronic disease management
> - Severe allergies or food sensitivities
> - Personalized medical treatment plans

**Known Limitations**:
- **Data Accuracy**: Nutrition data accuracy depends on dataset quality; preparation methods and ingredient sourcing affect values
- **Regional Coverage**: Currently focused on major Indian regions (North, South, East, West); some cuisines may have limited data
- **Allergies**: Always independently verify ingredients if you have severe allergies or food sensitivities
- **Portion Sizes**: Recommendations are approximate; actual portions depend on individual needs and cooking methods
- **Individual Variation**: Nutritional needs vary based on metabolism, health conditions, and medications
- **LLM Limitations**: AI recommendations may occasionally be inaccurate; always verify with nutritional references
- **GPU Acceleration**: Embeddings are faster with GPU support, but CPU execution is supported for moderate usage

**Best Practices**:
- Use this tool as a starting point for nutrition planning
- Cross-reference recommendations with official nutrition databases
- Keep your profile information updated for better recommendations
- Consult healthcare professionals for medical conditions
- Report any inaccurate nutritional data to help improve the system

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
