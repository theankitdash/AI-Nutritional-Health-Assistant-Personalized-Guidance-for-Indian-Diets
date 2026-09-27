# 🥗 AI Nutritional Health Assistant — Personalized Guidance for Indian Diets

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.1.6-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791.svg)](https://www.postgresql.org/)
[![Groq](https://img.shields.io/badge/Groq-LPU%20Inference-f55036.svg)](https://groq.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

An intelligent conversational AI nutrition assistant engineered specifically for Indian diets and regional food cultures. Powered by **FastAPI**, **LangGraph**, **Groq LPU high-speed inference**, and a two-stage **Hybrid Retrieval-Augmented Generation (RAG)** pipeline combining **BM25 sparse keyword retrieval**, **FAISS dense vector search**, **Reciprocal Rank Fusion (RRF)**, and **Cross-Encoder re-ranking**.

Features sub-millisecond local intent routing, an asynchronous single-call critical path, background conversation summarization, multi-tier caching (embedding cache, session cache, health metrics cache, and frontend TTL cache), and a sleek **Next.js 16 + TypeScript** responsive interface backed by **PostgreSQL 17**.

---

## ✨ Key Features

- 🍛 **Authentic Indian Regional Cuisines** — Deep contextual coverage of North, South, East, and West Indian culinary profiles, traditional preparations, and regional staples.
- ⚡ **Ultra-Fast Groq Inference** — Accelerated LLM processing via Groq LPUs (`qwen/qwen3.8-27b`, `openai/gpt-oss-120b`, or custom models) with zero GPU cost on your local machine.
- 🧠 **Instant Intent Classification (<1 ms)** — Local keyword rule-based routing that bypasses redundant LLM round-trips for maximum responsiveness.
- 🔍 **Two-Stage Hybrid RAG Pipeline** — Combines dense semantic search (FAISS + `all-MiniLM-L6-v2`) with sparse keyword matching (BM25), fused via Reciprocal Rank Fusion (RRF) and re-ranked using a Cross-Encoder (`ms-marco-MiniLM-L-6-v2`).
- 📈 **25+ Clinical & Health Metric Computations** — Computes BMI, BMR (Mifflin-St Jeor), Body Fat %, TDEE, Lean Body Mass, Visceral Fat, WHtR, Metabolic Age, macro/micronutrient splits, electrolytes, and hydration targets.
- 🏥 **Comprehensive Medical & Dietary Profiling** — Tracks allergies, chronic conditions (Diabetes, Hypertension, Thyroid, Cholesterol, Kidney, Liver, IBS, GERD, Gout, PCOS), spice tolerances, and lifestyle factors.
- 🛡️ **Robust Multi-Tier Caching** — Bounded in-memory FIFO query embedding cache, session-level profile cache, email-level health metrics cache, and frontend TTL cache (5 min).
- 🔒 **Secure Authentication & Session Handling** — HttpOnly cookie sessions, bcrypt password hashing, brute-force rate limiting (5 attempts / 5 mins), and direct SQL connection pooling with `asyncpg`.
- 💻 **Next.js 16 App Router UI** — Modern, accessible interface built with TypeScript, modular forms, live chat history, toast notifications, and customizable health profiles.
- 🐳 **Full Containerization** — Complete multi-service orchestration with Docker & Docker Compose, plus a one-click Windows launcher (`start-servers.bat`).

---

## 🏗️ Architecture & System Design

### Tech Stack

#### Backend
- **Framework**: FastAPI (ASGI with Uvicorn)
- **AI Orchestration**: LangGraph (StateGraph workflows, deterministic routing)
- **LLM Inference**: Groq API (`qwen/qwen3.8-27b` default, async non-blocking HTTP via `httpx`)
- **Dense Vector Search**: FAISS (`faiss-cpu`) with `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Sparse Keyword Search**: BM25 (`rank-bm25`) with pre-tokenized corpus
- **Ranking & Fusion**: Reciprocal Rank Fusion (RRF, $k=60$) + Cross-Encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) running in worker threads
- **Database & Pooling**: PostgreSQL 17 via `asyncpg.Pool` (`min_size=2, max_size=10`)
- **Security & Validation**: Pydantic v2, bcrypt password hashing, sliding-window rate limiting

#### Frontend
- **Framework**: Next.js 16.1 (App Router)
- **Library**: React 18
- **Language**: TypeScript 5.0+
- **Styling**: CSS Modules with modern design system and responsive layouts
- **State Management**: React Context (`AuthContext`, `ToastContext`), Custom Hook (`useModalForm`)
- **Client Cache**: In-memory TTL API cache (`apiCache.ts`, 5-minute TTL)

#### Infrastructure & Tools
- **Containerization**: Docker, Docker Compose (3 interconnected services: `frontend`, `fastapi`, `postgres-db`)
- **Diagnostics**: `test_groq_api.py`, `list_groq_models.py`
- **1-Click Startup**: `start-servers.bat` for Windows environments

---

### System Architecture Diagram

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
                          │ HTTP + HttpOnly Cookies (CORS localhost:3000 -> 8000)
                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                API LAYER (FastAPI)                             │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                  FastAPI Application (Uvicorn ASGI)                      │   │
│  │                                                                         │   │
│  │  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────────────┐   │   │
│  │  │  Auth Router   │  │  Chat Router    │  │  User Profile Router    │   │   │
│  │  │  /register/    │  │  /chat/         │  │  /personal-details/     │   │   │
│  │  │  /login/       │  │  (Background    │  │  /preferences/          │   │   │
│  │  │  /logout/      │  │   Summary Task) │  │  /health-conditions/     │   │   │
│  │  │  /check-login/ │  │                 │  │  /update-password/       │   │   │
│  │  └────────────────┘  └────────┬────────┘  └──────────────────────────┘   │   │
│  └───────────────────────────────┼──────────────────────────────────────────┘   │
└──────────────────────────────────┼──────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATION LAYER (LangGraph)                        │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                   Main Chat Graph (Fast Single-Call Path)                │   │
│  │                                                                         │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐     │   │
│  │  │  fetch_context_node (Multi-Tier In-Memory Cache)                │     │   │
│  │  │  • User Profile   -> Cached per Session (DB on cache miss)      │     │   │
│  │  │  • Health Metrics -> Cached per Email (Sub-graph on miss)       │     │   │
│  │  └────────────────────────────┬────────────────────────────────────┘     │   │
│  │                               ▼                                         │   │
│  │  ┌────────────────────────────────────────────────────────────────┐      │   │
│  │  │  classify_intent_node (Local Keyword Rules — <1 ms, NO LLM)    │      │   │
│  │  │  Routes: meal_plan | nutrition_query | health_advice | general │      │   │
│  │  └──────────┬───────────┬───────────────┬────────────────┬───────┘      │   │
│  │             │           │               │                │              │   │
│  │             ▼           ▼               ▼                ▼              │   │
│  │  ┌──────────────────────────────────────────────┐ ┌─────────────┐      │   │
│  │  │  search_food_node (Hybrid Search Pipeline)   │ │   General   │      │   │
│  │  │  • FAISS Dense (k=10) + BM25 Sparse (k=10)   │ │   Handler   │      │   │
│  │  │  • Reciprocal Rank Fusion (RRF, k=60)        │ │ (no search) │      │   │
│  │  │  • Cross-Encoder Re-ranker (thread executor) │ │             │      │   │
│  │  └──────┬───────────────────────┬───────────────┘ └──────┬──────┘      │   │
│  │         │                       │                        │             │   │
│  │         ▼                       ▼                        │             │   │
│  │  ┌──────────────┐        ┌──────────────┐                │             │   │
│  │  │  Meal Plan   │        │  Nutrition / │                │             │   │
│  │  │  Handler     │        │  Health Node │                │             │   │
│  │  └──────┬───────┘        └──────┬───────┘                │             │   │
│  │         │                       │                        │             │   │
│  │         └───────────────────────┴────────────────────────┘             │   │
│  │                                 │ (Only 1 LLM Call via Groq API)       │   │
│  │                                 ▼                                      │   │
│  │                           ┌──────────┐                                 │   │
│  │                           │   END    │  --> Immediate response to user │   │
│  │                           └──────────┘                                 │   │
│  │                                                                         │   │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │   │
│  │  │ BackgroundTasks: update_summary (Async non-blocking summarizer)   │  │   │
│  │  └───────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                  Health Metrics Graph (Sub-pipeline)                     │   │
│  │  fetch_user_data → compute_base_metrics (Age, BMI, BMR, BFP) →          │   │
│  │  compute_derived_metrics (TDEE, LBM, Muscle Mass, WHtR, etc.) →         │   │
│  │  compute_nutrition_metrics (Macros, Protein, Fiber, Electrolytes) →      │   │
│  │  finalize_metrics (Formats structured context for LLM prompt)           │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬──────────────────────┬──────────────────────────┘
                                 │                      │
                 ┌───────────────┘                      └──────────────┐
                 ▼                                                     ▼
┌────────────────────────────────┐         ┌───────────────────────────────────────┐
│       DATA / RAG LAYER         │         │              LLM LAYER                │
│                                │         │                                       │
│  ┌──────────────────────────┐  │         │  ┌────────────────────────────────┐   │
│  │  Hybrid Retrieval Engine │  │         │  │       Groq API Service         │   │
│  │  ┌────────────────────┐  │  │         │  │  ┌──────────────────────────┐  │   │
│  │  │ FAISS Dense Index  │  │  │         │  │  │  Default:                │  │   │
│  │  │ + BM25 Sparse      │  │  │         │  │  │  qwen/qwen3.8-27b        │  │   │
│  │  │ → RRF Fusion       │  │  │         │  │  │  (configurable via       │  │   │
│  │  │ → Cross-Encoder    │  │  │         │  │  │   GROQ_MODEL in .env)    │  │   │
│  │  │   Re-ranking       │  │  │         │  │  └──────────────────────────┘  │   │
│  │  └────────────────────┘  │  │         │  └────────────────────────────────┘   │
│  │  Files:                  │  │         │                                       │
│  │   app/food_dataset/      │  │         │  Used for: Response generation and    │
│  │   • index.faiss          │  │         │  conversation summarization           │
│  │   • bm25_corpus.json     │  │         └───────────────────────────────────────┘
│  │   • metadata.json        │  │
│  │   • index.json           │  │         ┌───────────────────────────────────────┐
│  └──────────────────────────┘  │         │          CACHING TIERS                │
│                                │         │                                       │
│  ┌──────────────────────────┐  │         │  ┌────────────────────────────────┐   │
│  │    PostgreSQL 17         │  │         │  │  Embedding Cache (_EMBEDDING)  │   │
│  │  ┌────────────────────┐  │  │         │  │  • FIFO cache (max 256 items)  │   │
│  │  │  credentials       │  │  │         │  ├────────────────────────────────┤   │
│  │  │  personal_details  │  │  │         │  │  Backend In-Memory Dicts       │   │
│  │  │  preferences       │  │  │         │  │  • user_profile_cache (session)│   │
│  │  │  health_conditions │  │  │         │  │  • health_metrics_cache (email)│   │
│  │  │  sessions          │  │  │         │  │  • conversation_summaries      │   │
│  │  │  (asyncpg pool)    │  │  │         │  ├────────────────────────────────┤   │
│  │  └────────────────────┘  │  │         │  │  Frontend API Cache (TTL 5 min)│   │
│  └──────────────────────────┘  │         │  │  • profile, prefs, health data │   │
│                                │         │  └────────────────────────────────┘   │
│  ┌──────────────────────────┐  │         └───────────────────────────────────────┘
│  │  Curated Food Datasets   │  │
│  │  • food_dataset.csv      │  │
│  │  • food_dataset.json     │  │
│  │  • Anuvaad.xlsx          │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
```

---

## 📁 Project Structure

```plaintext
.
├── app/                                 # FastAPI Backend Application
│   ├── food_dataset/                    # Pre-indexed search data
│   │   ├── index.faiss                  # FAISS dense vector index
│   │   ├── index.json                   # Food description documents
│   │   ├── metadata.json                # Nutritional metadata for items
│   │   └── bm25_corpus.json             # Pre-tokenized BM25 search corpus
│   ├── routers/                         # FastAPI route definitions
│   │   ├── auth.py                      # Authentication & rate-limited session management
│   │   ├── chat.py                      # Chat endpoint with BackgroundTasks summary
│   │   └── user_profile.py              # Profile, preferences, and health conditions CRUD
│   ├── services/                        # Core AI & retrieval logic
│   │   ├── graphs/                      # LangGraph workflow pipelines
│   │   │   ├── chat_graph.py            # Primary chat orchestration graph
│   │   │   ├── health_metrics_graph.py  # Health metrics computation graph
│   │   │   └── meal_planning_graph.py   # Dedicated meal plan generator graph
│   │   ├── nodes/                       # Graph nodes
│   │   │   ├── handler_nodes.py         # LLM response generation & summary nodes
│   │   │   ├── intent_nodes.py          # Fast local rule-based intent routing (<1 ms)
│   │   │   └── retrieval_nodes.py       # Context fetch and async hybrid food retrieval
│   │   ├── bm25_service.py              # BM25 sparse indexer & retriever
│   │   ├── cache.py                     # Profile and health metrics cache store
│   │   ├── faiss_service.py             # FAISS index loader & FIFO query embedding cache
│   │   ├── groq_api_service.py          # Groq API client with async httpx
│   │   ├── hybrid_retriever.py          # RRF fusion + non-blocking Cross-Encoder reranker
│   │   └── tools.py                     # LangChain-compatible food search tool
│   ├── db_connect.py                    # PostgreSQL schema init & asyncpg connection pool
│   ├── health_metrics.py                # 25+ clinical formulas and nutritional equations
│   ├── main.py                          # FastAPI ASGI entrypoint, CORS & startup lifespans
│   ├── models.py                        # Pydantic data validation schemas
│   ├── requirements.txt                 # Backend Python dependencies
│   ├── dockerfile                       # Backend container definition
│   └── .dockerignore                    # Docker build ignores
│
├── frontend/                            # Next.js 16 Frontend Application
│   ├── src/
│   │   ├── app/                         # App Router root pages and layouts
│   │   │   ├── layout.tsx               # Root application layout
│   │   │   └── page.tsx                 # Main application view with chat & modals
│   │   ├── components/                  # React modular components
│   │   │   ├── chat/                    # Chat interface (ChatContainer, ChatForm, ChatMessage)
│   │   │   ├── layout/                  # Navigation components (Header, Sidebar)
│   │   │   ├── modals/                  # Profile modals (PersonalDetails, Preferences, Health, Auth, Settings)
│   │   │   └── ui/                      # Base UI elements (Modal, Toast, FormComponents)
│   │   ├── contexts/                    # State contexts (AuthContext, ToastContext)
│   │   ├── hooks/                       # Custom hooks (useModalForm)
│   │   ├── lib/                         # Shared utilities, API client & TTL cache
│   │   │   ├── api.ts                   # Centralized API fetcher with cookie support
│   │   │   ├── apiCache.ts              # TTL-based client cache (5-minute expiry)
│   │   │   ├── formConstants.ts         # Options for diet, cuisine, and health forms
│   │   │   ├── types.ts                 # Full TypeScript interfaces
│   │   │   └── utils.ts                 # Form validation & helpers
│   │   └── styles/                      # CSS Modules for all components
│   ├── package.json                     # Frontend dependencies & scripts
│   ├── tsconfig.json                    # TypeScript configuration
│   ├── next.config.mjs                  # Next.js build configuration
│   ├── dockerfile                       # Multi-stage production frontend Docker image
│   └── .dockerignore                    # Frontend Docker build ignores
│
├── faiss_RAG.py                         # Offline index builder for FAISS + BM25 + metadata
├── food_dataset.csv                     # Raw Indian nutritional dataset (CSV)
├── food_dataset.json                    # Raw Indian nutritional dataset (JSON)
├── Food_dataset_Anuvaad.xlsx            # Multilingual regional food dataset
├── food_dataset.py                      # Dataset conversion script
├── usda-food.py                         # USDA nutritional data ingestion utility
├── list_groq_models.py                  # Utility to list active models on your Groq account
├── test_groq_api.py                     # Smoke test for Groq API connectivity
├── start-servers.bat                    # One-click Windows startup script
├── docker-compose.yml                   # 3-tier container orchestration configuration
├── API_CONNECTION_SETUP.md              # Frontend-backend networking guide
├── DOCKER_GUIDE.md                      # Detailed Docker deployment guide
├── .env                                 # Environment variables (DB credentials, API keys)
└── README.md                            # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Node.js 22+** and **npm**
- **PostgreSQL 17** (or run containerized via Docker)
- **Groq API Key** (Get one free at [console.groq.com](https://console.groq.com/))
- **Git**

---

### Option 1: 1-Click Startup (Windows)

If you are running Windows and have local Python, Node.js, and PostgreSQL configured:

```bat
start-servers.bat
```

This launches the FastAPI backend on port `8000` and the Next.js frontend on port `3000` in separate terminal windows.

---

### Option 2: Docker Compose (Recommended for Containerized Environments)

Ensure Docker Desktop is running, then run:

```bash
# Clone the repository
git clone https://github.com/theankitdash/AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets.git
cd AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets

# Build and start all 3 services
docker-compose up --build
```

**Services will be live at:**
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL**: `localhost:5432`

---

### Option 3: Manual Step-by-Step Setup

#### 1. Database Setup
Ensure PostgreSQL 17 is running. Create your database:

```sql
CREATE DATABASE nutrify_health;
```

#### 2. Configure Environment Variables
Create a `.env` file in the root directory (see [Configuration](#%EF%B8%8F-configuration)):

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nutrify_health
API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 3. Backend Setup

```bash
# Activate your Python virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r app/requirements.txt

# (Optional) Verify your Groq connection & model access
python test_groq_api.py

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Frontend Setup

In a separate terminal:

```bash
cd frontend

# Install Node dependencies
npm install

# Start Next.js development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```env
# ========================
# LLM Inference (Groq)
# ========================
GROQ_API_KEY=gsk_your_groq_api_key
GROQ_MODEL=qwen/qwen3.8-27b
# Alternative models: openai/gpt-oss-120b, openai/gpt-oss-20b, llama-3.3-70b-versatile

# ========================
# Database (PostgreSQL 17)
# ========================
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost            # Use 'postgres-db' when running in Docker
DB_PORT=5432
DB_NAME=nutrify_health

# ========================
# Application Networking
# ========================
API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000    # Docker: http://fastapi:8000
```

### Checking Available Groq Models

To see all available models supported on your Groq key:

```bash
python list_groq_models.py
```

---

## 🧠 Retrieval & Orchestration Deep Dive

### 1. Ultra-Low Latency Pipeline
- **Local Intent Classification**: Unlike traditional RAG pipelines that consume an extra LLM call for intent detection, this system utilizes high-efficiency keyword classification in `classify_intent_node`. It identifies queries as `meal_plan`, `nutrition_query`, `health_advice`, or `general` in **< 1 ms**.
- **Single Critical-Path LLM Call**: The user only waits for a single LLM response call.
- **Fire-and-Forget Conversation Summaries**: Summaries are updated out-of-band via FastAPI's `BackgroundTasks`, eliminating 2–5 seconds of blocking latency.

### 2. Two-Stage Hybrid Retrieval
1. **Stage 1 (Sparse + Dense Retrieval)**:
   - **BM25**: Tokenized lexical search ($k=10$) for exact dish names, ingredients, and regional terms.
   - **FAISS**: Dense semantic vector similarity ($k=10$) using `all-MiniLM-L6-v2` embeddings.
   - **Query Cache**: An in-memory bounded FIFO cache ($N=256$) ensures repeated questions bypass vector re-encoding.
2. **Reciprocal Rank Fusion (RRF)**:
   $$RRF\_Score(d) = \sum_{m \in \{FAISS, BM25\}} \frac{1}{60 + rank_m(d)}$$
3. **Stage 2 (Non-Blocking Cross-Encoder Re-Ranking)**:
   - Top candidates are re-scored using `cross-encoder/ms-marco-MiniLM-L-6-v2`.
   - Execution is offloaded to a background thread pool (`asyncio.to_thread` / `run_in_executor`) to prevent blocking the async event loop, returning the top 5 most relevant items.

### 3. Multi-Tier Caching System
- **Tier 1 (Client)**: 5-minute TTL cache in the Next.js frontend (`apiCache.ts`) avoiding redundant round-trips for profile and health conditions.
- **Tier 2 (Session)**: In-memory profile cache keyed by session ID.
- **Tier 3 (User)**: In-memory health metrics cache keyed by email; invalidated automatically whenever the user updates their profile.
- **Tier 4 (Vector)**: Embedding cache for query vectors in FAISS service.

---

## 📊 Dataset & Search Indexing

The nutritional knowledge base combines curated data from:
- **Indian Food Composition Tables (IFCT)**
- **USDA FoodData Central**
- **Anuvaad Regional Indian Dataset** (multilingual translations and preparation methods)

### Pre-built Indexes
The pre-processed indexes reside in `app/food_dataset/`:
- `index.faiss`: FAISS vector index of embeddings
- `bm25_corpus.json`: Pre-tokenized corpus for sparse retrieval
- `metadata.json`: Caloric, macronutrient, micronutrient, and regional attributes
- `index.json`: Full document text store

To rebuild or refresh the index from `food_dataset.csv`:
```bash
python faiss_RAG.py
```

---

## 📡 API Reference

### Authentication (`/app/routers/auth.py`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/register/` | Register new user with password complexity checks |
| `POST` | `/login/` | Authenticate user, apply rate-limiting, and set `session_id` cookie |
| `GET` | `/check-login/` | Check active session validity |
| `POST` | `/logout/` | Invalidate session in DB and clear cookie |
| `PUT` | `/update-password/` | Update user password |

### User Profile (`/app/routers/user_profile.py`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` / `POST` | `/personal-details/` | Get or update personal details (height, weight, waist, DOB, gender) |
| `GET` / `POST` | `/preferences/` | Get or update dietary and lifestyle preferences |
| `GET` / `POST` | `/health-conditions/` | Get or update health conditions (allergies, diabetes, PCOS, etc.) |

### Chat (`/app/routers/chat.py`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat/` | Send message to AI assistant; executes RAG graph and triggers background summary |

---

## ⚠️ Medical Disclaimer & Guidance

> [!WARNING]
> **Medical Disclaimer**: This application is strictly an educational and informational tool. It does **NOT** provide clinical medical diagnoses or prescribed medical nutrition therapy. Always consult a licensed healthcare professional, physician, or certified dietitian for medical conditions, severe allergies, or clinical treatment plans.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m "Add amazing feature"`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

Made with ❤️ for healthier Indian diets.
