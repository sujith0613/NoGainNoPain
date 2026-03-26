<div align="center">

# 🍽️ Food Market Intelligence & Decision Engine

### AI-powered full-stack system that transforms food market data into actionable business decisions

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-18+-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14+-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Claude](https://img.shields.io/badge/AI_Powered-Claude_API-D97706?style=for-the-badge&logoColor=white)

![NLP](https://img.shields.io/badge/NLP-VADER_Sentiment-8B5CF6?style=for-the-badge)
![Data](https://img.shields.io/badge/Data-1200%2B_Records-0EA5E9?style=for-the-badge)
![Cities](https://img.shields.io/badge/Cities-7_Indian_Cities-F59E0B?style=for-the-badge)
![Cuisines](https://img.shields.io/badge/Cuisines-15_Types-10B981?style=for-the-badge)
![APIs](https://img.shields.io/badge/Endpoints-14_APIs-EF4444?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-6B7280?style=for-the-badge)

![Status](https://img.shields.io/badge/Status-Hackathon_Build-22C55E?style=for-the-badge)
![Domain](https://img.shields.io/badge/Domain-Food_Intelligence-F97316?style=for-the-badge)
![Engine](https://img.shields.io/badge/Decision_Engine-Deterministic-7C3AED?style=for-the-badge)

</div>

---
```

---

An AI-powered full-stack system that transforms food market data into actionable business decisions.

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB running on `localhost:27017`

---

### 1. Start MongoDB

```bash
sudo systemctl start mongod
# or:
mongod --dbpath /var/lib/mongodb
```

---

### 2. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the server (auto-seeds DB on first run)
uvicorn main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:3000

---

## Project Structure

```
NoGainNoPain/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # MongoDB config
│   ├── requirements.txt
│   ├── data/
│   │   └── seed_data.py           # Generates 1200+ synthetic records
│   ├── data_pipeline/
│   │   ├── ingestion.py           # Stage 1: Load from MongoDB
│   │   ├── cleaning.py            # Stage 2: Null removal, type coercion
│   │   ├── normalization.py       # Stage 3: Min-Max scaling
│   │   ├── nlp_processing.py      # Stage 4: VADER sentiment + aspects
│   │   ├── feature_engineering.py # Stage 5: All derived features
│   │   └── scoring.py             # Stage 6: Opportunity/Risk/Profitability
│   ├── decision_engine/
│   │   ├── business_recommendation.py
│   │   ├── pricing_engine.py
│   │   ├── menu_generator.py
│   │   ├── demand_supply.py
│   │   ├── trend_engine.py
│   │   ├── sentiment_engine.py
│   │   ├── peak_hour_analyzer.py
│   │   ├── combo_engine.py
│   │   ├── scenario_simulator.py
│   │   ├── competitor_analysis.py
│   │   └── heatmap.py
│   └── routers/
│       ├── insights.py            # 10 market intelligence endpoints
│       └── competitor.py          # 4 competitor intelligence endpoints
└── frontend/
    ├── app/
    │   ├── page.tsx               # Landing page
    │   ├── start-business/        # New business dashboard
    │   └── improve-business/      # Competitor analysis dashboard
    └── lib/
        └── api.ts                 # Typed API client
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/business-recommendation` | Top cuisines to start by area + budget |
| `GET /api/pricing-analysis` | Optimal dish pricing |
| `GET /api/menu-generation` | Top dishes by demand score |
| `GET /api/demand-gap` | High demand, low supply opportunities |
| `GET /api/trend-analysis` | Rising/declining cuisine trends |
| `GET /api/sentiment-analysis` | Aspect-level sentiment (taste/service/price) |
| `GET /api/peak-hours` | Hourly demand distribution |
| `GET /api/combo-analysis` | Dish combination recommendations |
| `GET /api/scenario-simulation` | Business entry impact simulation |
| `GET /api/heatmap-data` | Area-level demand heatmap data |
| `GET /api/competitor-analysis` | Competitor identification & metrics |
| `GET /api/performance-score` | Restaurant rank & percentile |
| `GET /api/improvement-recommendations` | Prioritized improvement actions |
| `GET /api/gap-analysis` | Missing dishes & weak sentiment areas |

---

## Scoring Formulas

```
opportunity_score = (demand × sentiment × demand_growth) / supply_count
risk_score        = 0.4 × competition + 0.3 × negative_sentiment + 0.3 × |price_elasticity|
profitability     = avg_price × demand_score × max(sentiment, 0)
performance_score = 0.3×rating + 0.2×demand + 0.2×taste + 0.15×service + 0.15×growth
```

---

## Data Model

1200+ synthetic records across 7 Indian cities, 15 cuisine types, with:
- Core fields (restaurant, area, cuisine, dish, price, rating)
- NLP features (sentiment, taste, service, price scores)
- Demand/supply features
- Pricing intelligence (deviation, elasticity)
- Trend features (growth rates)
- Time intelligence (peak hours, weekends)
- Combo features (co-occurrence, association strength)
- Location intelligence (area demand, competition, rank)
