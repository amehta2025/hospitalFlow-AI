HospitalFlow AI
Real-time hospital operations intelligence platform that predicts Emergency Department boarding crises before they happen.

The Problem
ED boarding — when admitted patients wait in the emergency department for an inpatient bed — is one of the most well-documented patient safety crises in healthcare. Studies in PLOS One and Annals of Emergency Medicine link boarding directly to increased mortality. The average ED length of stay has grown from 5.6 hours pre-COVID to 8.5 hours in 2023 and hasn't recovered.
The data to predict these crises already exists in hospital systems. The problem is it's fragmented across EHRs, bed management systems, and lab systems — and nobody is watching all of it simultaneously in real time.
HospitalFlow AI is a proof-of-concept platform that unifies those streams, detects anomalies, predicts risk, and explains what's happening in plain English.

What It Does

Ingests a real-time stream of simulated hospital events (patient arrivals, lab results, discharges, ICU updates)
Detects operational anomalies across ED, ICU, lab, transport, and discharge using rule-based thresholds
Predicts ED boarding crisis risk using a trained Random Forest model
Explains the current situation using GPT-4o-mini, generating plain-English summaries with actionable recommendations
Displays everything on a live React dashboard that updates every 15 seconds


Architecture
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

Tech Stack
LayerTechnologyBackendPython, FastAPI, SQLAlchemyDatabasePostgreSQLMLscikit-learn (Random Forest), StandardScalerAIOpenAI GPT-4o-miniFrontendReact, RechartsInfrastructureDocker-ready, deployable to AWS/Fly.io

Key Features
Time-windowed metrics — all metrics computed over a rolling 10-minute window so the system reflects current hospital state, not historical averages.
Multi-signal anomaly detection — monitors ED wait time, ICU pressure, lab turnaround, discharge backlog, transport delays, and high-severity event rate simultaneously.
ML risk prediction — Random Forest trained on scenario-based synthetic data predicts ED boarding crisis probability with top contributing factors and feature importances.
LLM incident summary — structured metrics fed to GPT-4o-mini generate a 3-4 sentence clinical narrative with specific numbers and recommended actions for operations managers.
Live dashboard — color-coded metric cards, real-time trend chart, active alerts panel, AI summary, and ML risk score — all auto-updating.

Running Locally
Prerequisites: Python 3.13+, Node.js 18+, PostgreSQL
bash# Clone the repo
git clone https://github.com/amehta2025/hospitalFlow-AI.git
cd hospitalFlow-AI

# Backend setup
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Add environment variables
# Create a .env file with:
# DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/hospitalflow
# OPENAI_API_KEY=your_openai_key

# Create the database
psql -U postgres -c "CREATE DATABASE hospitalflow;"

# Start the backend
uvicorn backend.main:app --reload

# In a second terminal, start the simulator
python -c "from backend.simulator.simulator import run_simulator; run_simulator()"

# In a third terminal, start the frontend
cd frontend
npm install
npm start
Visit http://localhost:3000 to see the live dashboard.

API Endpoints
EndpointDescriptionGET /Health checkPOST /eventsIngest a hospital eventGET /metrics/liveCurrent metrics (10-min window)GET /alertsActive anomaly alertsGET /predictML risk predictionGET /summaryFull pipeline: metrics + alerts + prediction + AI summary

Honest Limitations

Training data is synthetic, generated from simulator scenarios rather than real EHR data. A production system would retrain on labeled historical incident data.
The 10-minute event window tracks operational activity patterns, not individual patient wait times end-to-end. A production system would maintain patient-level state.
Anomaly thresholds are clinically informed estimates, not validated against real hospital outcome data.


Research Background
This project addresses a well-documented clinical operations problem:

ED boarding associated with increased in-hospital mortality (PLOS One, 2020)
Average ED length of stay increased 52% post-COVID and has not recovered (Emergency Medicine Literature, 2023)
AHRQ issued a Special Emphasis Notice for research specifically targeting ED boarding and hospital crowding
Real-time discharge volume prediction shown to reduce ED boarding times (JMIR, 2025)


Built by Anish Mehta — CS @ UIUC
