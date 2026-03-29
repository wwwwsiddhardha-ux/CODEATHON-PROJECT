# 📊 Skill Investment Portfolio Engine

> Treat your skills like financial investments. Analyze your profile against real-time market demand and get AI-powered portfolio allocation recommendations.

---

## 🏗️ Architecture

```
CODEATHON-PROJECT/
├── backend/
│   ├── app.py                    # FastAPI entry point
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── models/
│   │   └── schemas.py            # Pydantic request/response models
│   ├── routers/
│   │   ├── profile.py            # User profile CRUD
│   │   ├── market.py             # Market demand endpoint
│   │   ├── recommendations.py    # Full pipeline endpoint
│   │   └── roadmap.py            # Weekly plan endpoint
│   └── services/
│       ├── scraping_service.py   # Bright Data integration
│       ├── ai_service.py         # Featherless AI integration
│       └── scoring_engine.py     # Risk/Reward scoring logic
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Root component + orchestration
│   │   ├── api/client.js         # Axios API client
│   │   └── components/
│   │       ├── ProfileForm.jsx       # User input form
│   │       ├── SkillPieChart.jsx     # Portfolio allocation pie chart
│   │       ├── RiskRewardChart.jsx   # Risk vs Reward scatter plot
│   │       ├── RecommendationPanel.jsx # AI invest/reduce advice
│   │       ├── WeeklyRoadmap.jsx     # Weekly hour allocation
│   │       └── MarketTrends.jsx      # Demand signal bars
│   ├── Dockerfile
│   └── package.json
├── database/
│   └── firestore.py              # Firestore persistence helpers
├── docker-compose.yml
├── deploy.sh                     # Google Cloud Run deploy script
└── README.md
```

---

## ⚡ Quick Start (Local)

### 1. Clone & configure environment

```bash
cd backend
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Run Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 3. Run Frontend (React)

```bash
cd frontend
npm install
npm start
```

App available at: http://localhost:3000

### 4. Run with Docker Compose (recommended)

```bash
# From project root
docker-compose up --build
```

---

## 🔑 API Keys Setup

| Key | Where to get |
|-----|-------------|
| `BRIGHT_DATA_API_KEY` | [brightdata.com](https://brightdata.com) → API Access |
| `FEATHERLESS_API_KEY` | [featherless.ai](https://featherless.ai) → Dashboard |
| `GOOGLE_CLOUD_PROJECT` | GCP Console → Project ID |

> **No API keys?** The app works fully with mock data for local demo.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/recommendations/` | Full pipeline: score + AI advice |
| `POST` | `/api/roadmap/` | Weekly learning plan |
| `POST` | `/api/market/demand` | Real-time market demand |
| `POST` | `/api/profile/` | Save user profile |
| `GET`  | `/api/profile/{name}` | Get saved profile |

### Example Request

```json
POST /api/recommendations/
{
  "name": "Alex",
  "skills": [
    {"name": "Python", "proficiency": 8},
    {"name": "Docker", "proficiency": 5},
    {"name": "AWS", "proficiency": 4}
  ],
  "interests": ["cloud", "AI"],
  "career_goal": "DevOps Engineer",
  "hours_per_week": 20
}
```

---

## ☁️ Deploy to Google Cloud Run

### Prerequisites

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com containerregistry.googleapis.com
```

### Deploy

```bash
export BRIGHT_DATA_API_KEY=your_key
export FEATHERLESS_API_KEY=your_key
bash deploy.sh
```

---

## 🧠 Scoring Logic

```
For each skill:
  demand_score    = from Bright Data (job frequency, normalized 0–10)
  growth_potential = (10 - proficiency) / 10 × demand_score
  learning_difficulty = static map (Python=3, Kubernetes=7, etc.)

  risk_score   = (difficulty + (10 - demand)) / 2
  reward_score = (demand + salary_normalized) / 2

  allocation % = reward/risk ratio, normalized across all skills
```

---

## 🛠️ Tech Stack

- **Frontend**: React 18, Tailwind CSS, Recharts
- **Backend**: FastAPI, Python 3.11
- **AI**: Featherless AI (Llama 3.1 8B)
- **Scraping**: Bright Data Web Unlocker API
- **Cloud**: Google Cloud Run + Firestore
- **Containers**: Docker + Docker Compose
