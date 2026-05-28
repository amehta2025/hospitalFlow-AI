from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from backend.database import engine, Base, get_db
from backend.models import HospitalEvent
from pydantic import BaseModel
from backend.summarizer import generate_summary
from backend.predictor import predict_risk

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
class EventIn(BaseModel):
    timestamp: str
    event_type: str
    department: str
    patient_id: str
    wait_time_minutes: float
    severity: int
    scenario: str

@app.get("/")
def root():
    return {"status": "HospitalFlow API is running"}


@app.post("/events")
def create_event(event: EventIn, db: Session = Depends(get_db)):
    db_event = HospitalEvent(
        timestamp=datetime.fromisoformat(event.timestamp),
        event_type=event.event_type,
        department=event.department,
        patient_id=event.patient_id,
        wait_time_minutes=event.wait_time_minutes,
        severity=event.severity,
        scenario=event.scenario,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return {"status": "ok", "id": db_event.id}


@app.get("/metrics/live")
def live_metrics(db: Session = Depends(get_db)):
    total_events = db.query(HospitalEvent).count()

    avg_wait = db.query(func.avg(HospitalEvent.wait_time_minutes)).scalar() or 0

    ed_avg_wait = db.query(func.avg(HospitalEvent.wait_time_minutes))\
        .filter(HospitalEvent.department == "ED").scalar() or 0

    recent_events = db.query(HospitalEvent)\
        .order_by(HospitalEvent.timestamp.desc()).limit(5).all()

    return {
        "total_events": total_events,
        "avg_wait_minutes": round(avg_wait, 1),
        "ed_avg_wait_minutes": round(ed_avg_wait, 1),
        "recent_events": [
            {
                "event_type": e.event_type,
                "department": e.department,
                "patient_id": e.patient_id,
                "wait_time_minutes": e.wait_time_minutes,
                "severity": e.severity,
            }
            for e in recent_events
        ]
    }


@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    from backend.alerts import compute_metrics, detect_anomalies
    metrics = compute_metrics(db)
    alerts = detect_anomalies(metrics)
    return {"metrics": metrics, "alerts": alerts}

@app.get("/predict")
def get_prediction(db: Session = Depends(get_db)):
    from backend.alerts import compute_metrics
    metrics = compute_metrics(db)
    prediction = predict_risk(metrics)
    return prediction

@app.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    from backend.alerts import compute_metrics, detect_anomalies
    from backend.predictor import predict_risk
    metrics = compute_metrics(db)
    alerts = detect_anomalies(metrics)
    prediction = predict_risk(metrics)
    summary = generate_summary(metrics, alerts, prediction)
    return {"summary": summary, "metrics": metrics, "alerts": alerts, "prediction": prediction}