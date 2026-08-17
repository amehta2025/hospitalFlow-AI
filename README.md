# HospitalFlow AI

Real-time hospital operations intelligence platform that predicts Emergency Department boarding crises before they happen.

**[Live Demo](https://hospital-flow-ai-six.vercel.app)**

> The first load may take up to 60 seconds.

---

## The Problem

ED boarding (when admitted patients wait in the emergency department for an inpatient bed) is one of the most documented patient safety crises in healthcare. Studies link boarding directly to increased mortality. The average ED length of stay has grown from 5.6 hours pre-COVID to 8.5 hours in 2023 and has not recovered.

The data to predict these crises already exists in hospital systems. The problem is it is fragmented across EHRs, bed management systems, and lab systems; however, nobody is or can watch it all simultaneously in real time.

HospitalFlow AI is a proof-of-concept platform that unifies those streams, detects anomalies, predicts risk, and explains what is happening in plain English.

---

## What It Does

- Ingests a real-time stream of simulated hospital events (patient arrivals, lab results, discharges, ICU updates)
- Detects operational anomalies across ED, ICU, lab, transport, and discharge using rule-based thresholds
- Predicts ED boarding crisis risk using a trained Random Forest model
- Explains the current situation using GPT-4o-mini, generating plain-English summaries with actionable recommendations
- Displays everything on a live React dashboard that updates every 15 seconds

---

## Architecture

```
Browser
   ↓
React Dashboard (Vercel) — live, auto-refreshing every 15s
   ↓  HTTPS / REST
FastAPI Backend (Render)
   ├── Event Simulator (background thread)  →  POST /events
   ├── Rule-Based Anomaly Detection         →  Alerts
   ├── ML Risk Predictor                    →  Risk Score + Top Factors
   └── LLM Summarizer (GPT-4o-mini)         →  Plain-English Incident Summary
   ↓  SQL over TLS
PostgreSQL (Neon)
```

Each layer talks only to the layer below it — the frontend never touches the database directly; all access is mediated by the API.

---

## Tech Stack

| Layer | Technology | Hosted On |
|---|---|---|
| Frontend | React, Recharts, axios | Vercel |
| Backend | Python, FastAPI, SQLAlchemy | Render |
| Database | PostgreSQL | Neon |
| ML | scikit-learn (Random Forest) | — |
| AI | OpenAI GPT-4o-mini | — |

---

## Key Features

**10-minute window metrics** — all metrics computed over a rolling 10-minute window so the system displays the current hospital state, not historical averages.

**Multi-signal anomaly detection** — monitors ED wait time, ICU pressure, lab turnaround, discharge backlog, transport delays, and high-severity event rate simultaneously.

**ML risk prediction** — Random Forest trained on scenario-based synthetic data predicts ED boarding crisis probability with top contributing factors and feature importances.

**LLM incident summary** — structured metrics fed to GPT-4o-mini generate a 3-4 sentence clinical narrative with specific numbers and recommended actions for operations managers. Responses are cached server-side (3-minute TTL) so API cost stays flat regardless of traffic.

**Live dashboard** — color-coded metric cards, real-time trend chart, active alerts panel, AI summary, and ML risk score — all auto-updating.

---

## Running Locally

**Prerequisites:** Python 3.13+, Node.js 18+, PostgreSQL

**1. Clone the repo**

```bash
git clone https://github.com/amehta2025/hospitalFlow-AI.git
cd hospitalFlow-AI
```

**2. Set up the backend**

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**3. Create a `.env` file in the root directory**

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/hospitalflow
OPENAI_API_KEY=your_openai_key
```

**4. Create the database**

```bash
psql -U postgres -c "CREATE DATABASE hospitalflow;"
```

**5. Start the backend server**

The event simulator starts automatically as a background thread via the FastAPI lifespan handler.

```bash
uvicorn backend.main:app --reload
```

**6. Start the frontend (new terminal)**

```bash
cd frontend
npm install
npm start
```

Visit `http://localhost:3000` to see the live dashboard. The frontend reads `REACT_APP_API_URL` and falls back to `http://127.0.0.1:8000` for local development.

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Health check |
| `POST /events` | Ingest a hospital event |
| `GET /metrics/live` | Current metrics (10-min window) |
| `GET /alerts` | Active anomaly alerts |
| `GET /predict` | ML risk prediction |
| `GET /summary` | Full pipeline: metrics + alerts + prediction + AI summary |

---


## Where This Could Go

Running this service across several hospitals can drive routing decisions EMS can act on before diversion becomes necessary. That shifts the system from monitoring to load balancing, and is the direction this architecture was built to support.

---

## Research Background

- ED boarding associated with increased in-hospital mortality
- Average ED length of stay increased 52% post-COVID and has not recovered
- AHRQ issued a Special Emphasis Notice for research specifically targeting ED boarding
- Real-time discharge volume prediction shown to reduce ED boarding times

---

Developed by Anish Mehta; CS + Chem @ UIUC
