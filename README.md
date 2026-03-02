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
- **LangGraph** — Advanced workflow orchestration for AI agent pipelines
- **LangChain** — LLM application framework (Document, VectorStore, Embeddings)
- **FAISS** — Vector similarity search for RAG pipeline
- **Sentence Transformers** — Text embeddings (`all-MiniLM-L6-v2`, HuggingFace)
- **PostgreSQL 17** — Relational storage for users, profiles, sessions
- **asyncpg** — Async PostgreSQL adapter (direct SQL, no ORM)
- **Pydantic** — Request/response data validation
- **bcrypt** — Password hashing for authentication
- **NVIDIA NIM API** — LLM inference endpoint (`google/gemma-3-27b-it`)

#### Frontend
- **Next.js 16** — React framework with App Router
- **React 18** — Modern UI library
- **TypeScript 5.0+** — Type-safe JavaScript
- **CSS Modules** — Scoped component-level styles

#### Infrastructure
- **Docker & Docker Compose** — Multi-container orchestration (3 services)
- **PostgreSQL 17** — Containerized database with persistent volume
- **Uvicorn** — ASGI server for FastAPI
- **NVIDIA API Endpoints** — Cloud LLM inference

### System Design

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                                │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                     Next.js 16 Frontend (TypeScript)                     │  │
│  │                                                                         │  │
│  │  ┌────────────┐  ┌───────────────┐  ┌──────────────┐  ┌─────────────┐   │  │
│  │  │ AuthModal  │  │ PersonalDet.  │  │ Preferences  │  │ HealthCond. │   │  │
│  │  │            │  │    Modal      │  │    Modal     │  │    Modal    │   │  │
│  │  └────────────┘  └───────────────┘  └──────────────┘  └─────────────┘   │  │
│  │  ┌──────────────────────────────────────┐  ┌────────────────────────┐    │  │
│  │  │  ChatContainer + ChatForm + Message  │  │  Header + Sidebar     │    │  │
│  │  └──────────────────────────────────────┘  └────────────────────────┘    │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐   │  │
│  │  │  AuthContext      │  │  ToastContext    │  │  useModalForm Hook  │   │  │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────────────────────┘
                          │ HTTP + Cookies (CORS)
                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                API LAYER                                       │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                  FastAPI Application (Uvicorn ASGI)                      │   │
│  │                                                                         │   │
│  │  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────────────┐   │   │
│  │  │  Auth Router   │  │  Chat Router    │  │  User Profile Router    │   │   │
│  │  │  /register     │  │  /chat/         │  │  /personal-details      │   │   │
│  │  │  /login        │  │                 │  │  /preferences           │   │   │
│  │  │  /logout       │  │                 │  │  /health-conditions     │   │   │
│  │  │  /check-login  │  │                 │  │  GET + POST endpoints   │   │   │
│  │  │  /update-pass  │  │                 │  │                         │   │   │
│  │  └────────────────┘  └────────┬────────┘  └──────────────────────────┘   │   │
│  └───────────────────────────────┼──────────────────────────────────────────┘   │
└──────────────────────────────────┼──────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATION LAYER (LangGraph)                        │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                        Chat Graph (Main Pipeline)                       │   │
│  │                                                                         │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐     │   │
│  │  │              Parallel Retrieval Node (asyncio.gather)           │     │   │
│  │  │  ┌──────────────┐ ┌───────────────────┐ ┌───────────────────┐  │     │   │
│  │  │  │ Retrieve     │ │ Compute Health    │ │ Retrieve Food     │  │     │   │
│  │  │  │ User Profile │ │ Metrics (sub-graph)│ │ (FAISS Search)    │  │     │   │
│  │  │  └──────────────┘ └───────────────────┘ └───────────────────┘  │     │   │
│  │  └────────────────────────────┬────────────────────────────────────┘     │   │
│  │                               ▼                                         │   │
│  │  ┌────────────────────────────────────────────────────────────────┐      │   │
│  │  │         Intent Classification Node (LLM-powered)              │      │   │
│  │  │    Classifies: meal_plan | nutrition_query | health_advice |   │      │   │
│  │  │                 general                                       │      │   │
│  │  └──────────┬───────────┬───────────────┬────────────────┬───────┘      │   │
│  │             ▼           ▼               ▼                ▼              │   │
│  │  ┌──────────────┐ ┌────────────┐ ┌──────────────┐ ┌─────────────┐      │   │
│  │  │  Meal Plan   │ │ Nutrition  │ │   Health     │ │   General   │      │   │
│  │  │  Handler ─────▶│  Query     │ │   Advice     │ │   Handler   │      │   │
│  │  │(sub-graph)   │ │  Handler   │ │   Handler    │ │             │      │   │
│  │  └──────┬───────┘ └─────┬──────┘ └──────┬───────┘ └──────┬──────┘      │   │
│  │         └───────────────┴───────────────┴────────────────┘              │   │
│  │                                    ▼                                    │   │
│  │                    ┌──────────────────────────┐                          │   │
│  │                    │  Summary Node (LLM)      │                          │   │
│  │                    │  Updates conversation    │                          │   │
│  │                    │  summary for memory      │                          │   │
│  │                    └──────────────────────────┘                          │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                     Meal Planning Graph (Sub-pipeline)                   │   │
│  │  analyze_requirements → fetch_health_metrics → fetch_food_context →      │   │
│  │  generate_meals (LLM) → validate_nutrition (LLM) → format_meal_plan     │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                  Health Metrics Graph (Sub-pipeline)                     │   │
│  │  fetch_user_data → compute_base_metrics (Age, BMI, BMR, BFP) →          │   │
│  │  compute_derived_metrics (TDEE, LBM, Muscle Mass, WHtR, etc.) →         │   │
│  │  compute_nutrition_metrics (Macros, Protein, Fiber, Electrolytes) →      │   │
│  │  finalize_metrics (format for LLM context)                              │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬──────────────────────┬──────────────────────────┘
                                 │                      │
                 ┌───────────────┘                      └──────────────┐
                 ▼                                                     ▼
┌────────────────────────────────┐         ┌───────────────────────────────────────┐
│       DATA / RAG LAYER         │         │              LLM LAYER                │
│                                │         │                                       │
│  ┌──────────────────────────┐  │         │  ┌────────────────────────────────┐   │
│  │    FAISS Vector Index    │  │         │  │     NVIDIA NIM API Service     │   │
│  │  ┌────────────────────┐  │  │         │  │  ┌──────────────────────────┐  │   │
│  │  │ index.faiss        │  │  │         │  │  │  Model: google/gemma-3-  │  │   │
│  │  │ index.json         │  │  │         │  │  │         27b-it           │  │   │
│  │  └────────────────────┘  │  │         │  │  │                          │  │   │
│  │  Sentence Transformers   │  │         │  │  │                          │  │   │
│  │  (all-MiniLM-L6-v2)      │  │         │  │  └──────────────────────────┘  │   │
│  └──────────────────────────┘  │         │  └────────────────────────────────┘   │
│                                │         │                                       │
│  ┌──────────────────────────┐  │         │  Used for: Intent Classification,     │
│  │    PostgreSQL 17         │  │         │  Meal Planning, Nutrition Queries,    │
│  │  ┌────────────────────┐  │  │         │  Health Advice, Conversation Summary  │
│  │  │  credentials       │  │  │         └───────────────────────────────────────┘
│  │  │  personal_details  │  │  │
│  │  │  preferences       │  │  │         ┌───────────────────────────────────────┐
│  │  │  health_conditions │  │  │         │          CACHING LAYER                │ 
│  │  │  sessions          │  │  │         │                                       │
│  │  └────────────────────┘  │  │         │  ┌────────────────────────────────┐   │
│  └──────────────────────────┘  │         │  │  In-Memory Python Dicts        │   │
│                                │         │  │  • user_profile_cache(by sess) │   │
│  ┌──────────────────────────┐  │         │  │  • conversation_summaries      │   │
│  │  Food Datasets (Source)  │  │         │  └────────────────────────────────┘   │
│  │  • food_dataset.csv      │  │         └───────────────────────────────────────┘
│  │  • food_dataset.json     │  │
│  │  • Anuvaad.xlsx          │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
```

**Chat Pipeline Flow (LangGraph):**
1. User message arrives at `/chat/` endpoint → session validated via cookie
2. **Parallel Retrieval** — User profile, health metrics, and FAISS food search run concurrently (`asyncio.gather`)
3. **Intent Classification** — LLM classifies intent into `meal_plan`, `nutrition_query`, `health_advice`, or `general`
4. **Conditional Routing** — Message routed to the appropriate specialized handler node
5. **Handler Execution** — Handler generates response using user context + health metrics + food data + LLM
6. **Summary Update** — Conversation summary updated for multi-turn memory
7. Response returned to frontend

**Health Metrics Pipeline (25+ Calculations):**
- Base: Age, BMI, BMR (Mifflin-St Jeor), Body Fat %
- Derived: TDEE, Lean Body Mass, Muscle Mass, Visceral Fat, WHtR, Metabolic Age
- Nutrition: Macronutrient breakdown, Protein intake, Micronutrients, Electrolytes, Fiber
- Assessment: BMD, Max Heart Rate, Hydration Level, Sleep Score, Skeletal Muscle Mass

---

## 📁 Project Structure

```plaintext
.
├── app/                              # FastAPI Backend
│   ├── routers/                      # API route handlers
│   │   ├── auth.py                   # Authentication (register, login, logout, sessions)
│   │   ├── chat.py                   # Chat endpoint (POST /chat/)
│   │   └── user_profile.py           # Profile CRUD (personal, preferences, health)
│   ├── services/                     # Business logic & AI services
│   │   ├── graphs/                   # LangGraph pipeline definitions
│   │   │   ├── chat_graph.py         # Main chat orchestration graph
│   │   │   ├── health_metrics_graph.py  # Health metrics computation graph
│   │   │   └── meal_planning_graph.py   # Meal plan generation graph
│   │   ├── nodes/                    # LangGraph node implementations
│   │   │   ├── intent_nodes.py       # Intent classification & routing
│   │   │   ├── retrieval_nodes.py    # User, health, food data retrieval
│   │   │   └── handler_nodes.py      # Specialized response handlers
│   │   ├── faiss_service.py          # FAISS index loading & search
│   │   ├── nvidia_api_service.py     # NVIDIA NIM API integration
│   │   └── cache.py                  # In-memory session caching
│   ├── food_dataset/                 # Pre-built FAISS index
│   │   ├── index.faiss               # FAISS vector index (1.5MB)
│   │   ├── index.json                # Food text data for docstore
│   │   └── food_dataset.csv          # Original CSV for FAISS build
│   ├── main.py                       # FastAPI app entry point + CORS + startup
│   ├── models.py                     # Pydantic request/response models
│   ├── db_connect.py                 # PostgreSQL connection + table creation
│   ├── health_metrics.py             # 25+ health metric calculators
│   ├── requirements.txt              # Python dependencies
│   ├── dockerfile                    # Backend Docker image
│   └── .dockerignore                 # Docker build exclusions
│
├── frontend/                         # Next.js 16 Frontend
│   ├── src/
│   │   ├── app/                      # Next.js App Router
│   │   │   ├── layout.tsx            # Root layout
│   │   │   └── page.tsx              # Main page (chat interface)
│   │   ├── components/               # React components
│   │   │   ├── chat/                 # Chat UI components
│   │   │   │   ├── ChatContainer.tsx # Chat window with message history
│   │   │   │   ├── ChatForm.tsx      # Message input form
│   │   │   │   └── ChatMessage.tsx   # Individual message bubble
│   │   │   ├── layout/               # Layout components
│   │   │   │   ├── Header.tsx        # App header with navigation
│   │   │   │   └── Sidebar.tsx       # Side navigation panel
│   │   │   ├── modals/               # Modal dialogs
│   │   │   │   ├── AuthModal.tsx     # Login/Register modal
│   │   │   │   ├── PersonalDetailsModal.tsx
│   │   │   │   ├── PreferencesModal.tsx
│   │   │   │   ├── HealthConditionsModal.tsx
│   │   │   │   └── AccountSettingsModal.tsx
│   │   │   └── ui/                   # Shared UI primitives
│   │   │       ├── Modal.tsx         # Base modal component
│   │   │       ├── FormComponents.tsx # Reusable form elements
│   │   │       └── Toast.tsx         # Toast notifications
│   │   ├── contexts/                 # React Contexts
│   │   │   ├── AuthContext.tsx       # Authentication state management
│   │   │   └── ToastContext.tsx      # Toast notification state
│   │   ├── hooks/                    # Custom React hooks
│   │   │   └── useModalForm.ts       # Form state management for modals
│   │   └── styles/                   # CSS Modules
│   │       ├── globals.css           # Global styles
│   │       └── components/           # Component-scoped styles
│   │           ├── Chat.module.css
│   │           ├── Header.module.css
│   │           ├── MainPage.module.css
│   │           ├── Modal.module.css
│   │           ├── Sidebar.module.css
│   │           └── Toast.module.css
│   ├── package.json                  # Node.js dependencies
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── next.config.mjs               # Next.js configuration
│   ├── dockerfile                    # Frontend Docker image
│   └── .dockerignore                 # Docker build exclusions
│
├── faiss_RAG.py                      # Standalone FAISS index builder script
├── food_dataset.csv                  # Curated Indian food nutrition data
├── food_dataset.json                 # JSON format food data (3.4MB)
├── Food_dataset_Anuvaad.xlsx         # Regional dataset with translations
├── food_dataset.py                   # Dataset conversion utility
├── usda-food.py                      # USDA food data fetcher
├── test_nvidia_api.py                # NVIDIA API connection test
├── docker-compose.yml                # Multi-container orchestration (3 services)
├── start-servers.bat                 # Quick start script (Windows)
├── API_CONNECTION_SETUP.md           # API setup guide
├── DOCKER_GUIDE.md                   # Docker deployment guide
├── .env                              # Environment variables
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
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
