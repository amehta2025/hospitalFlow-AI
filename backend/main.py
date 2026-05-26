from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from backend.database import engine, Base, get_db
from backend.models import HospitalEvent
from pydantic import BaseModel

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow frontend to talk to backend later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schema for incoming events ---
class EventIn(BaseModel):
    timestamp: str
    event_type: str
    department: str
    patient_id: str
    wait_time_minutes: float
    severity: int
    scenario: str


# --- Routes ---
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
    alerts = []

    ed_avg_wait = db.query(func.avg(HospitalEvent.wait_time_minutes))\
        .filter(HospitalEvent.department == "ED").scalar() or 0

    if ed_avg_wait > 90:
        alerts.append({
            "level": "critical",
            "message": f"ED average wait time is {round(ed_avg_wait, 1)} minutes — exceeds 90 minute threshold"
        })
    elif ed_avg_wait > 60:
        alerts.append({
            "level": "warning",
            "message": f"ED average wait time is {round(ed_avg_wait, 1)} minutes — approaching critical threshold"
        })

    if not alerts:
        alerts.append({
            "level": "ok",
            "message": "All systems normal"
        })

    return {"alerts": alerts}