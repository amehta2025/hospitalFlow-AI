# HospitalFlow AI

Real-time hospital operations intelligence platform that predicts Emergency Department boarding crises before they happen.

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
Hospital Event Simulator
        ↓
FastAPI Backend (REST API)
        ↓
PostgreSQL Database
        ↓
Rule-Based Anomaly Detection  →  Alerts
ML Risk Predictor             →  Risk Score + Top Factors
LLM Summarizer (GPT-4o-mini)  →  Plain-English Incident Summary
        ↓
React Dashboard (live, auto-refreshing)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| ML | scikit-learn (Random Forest) |
| AI | OpenAI GPT-4o-mini |
| Frontend | React, Recharts |

---

## Key Features

**10-minute window metrics** — all metrics computed over a rolling 10-minute window so the system displays the current hospital state, not historical averages.

**Multi-signal anomaly detection** — monitors ED wait time, ICU pressure, lab turnaround, discharge backlog, transport delays, and high-severity event rate simultaneously.

**ML risk prediction** — Random Forest trained on scenario-based synthetic data predicts ED boarding crisis probability with top contributing factors and feature importances.

**LLM incident summary** — structured metrics fed to GPT-4o-mini generate a 3-4 sentence clinical narrative with specific numbers and recommended actions for operations managers.

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

```bash
uvicorn backend.main:app --reload
```

**6. Start the simulator (new terminal)**

```bash
venv\Scripts\activate
python -c "from backend.simulator.simulator import run_simulator; run_simulator()"
```

**7. Start the frontend (new terminal)**

```bash
cd frontend
npm install
npm start
```

Visit `http://localhost:3000` to see the live dashboard.

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

## Honest Limitations

- Training data is synthetic, generated from simulator scenarios rather than real EHR data. A production system would retrain on labeled historical incident data.
- The 10-minute event window tracks operational activity patterns, not individual patient wait times end-to-end.
- Anomaly thresholds are clinically informed estimates, not validated against real hospital outcome data.

---

## Research Background

- ED boarding associated with increased in-hospital mortality 
- Average ED length of stay increased 52% post-COVID and has not recovered
- AHRQ issued a Special Emphasis Notice for research specifically targeting ED boarding
- Real-time discharge volume prediction shown to reduce ED boarding times 

---

Developed by Anish Mehta; CS + Chem @ UIUC
