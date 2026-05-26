from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models import HospitalEvent


def compute_metrics(db: Session) -> dict:
    """Compute current hospital metrics from the database."""

    # Overall average wait
    avg_wait = db.query(func.avg(HospitalEvent.wait_time_minutes)).scalar() or 0

    # ED specific
    ed_avg_wait = db.query(func.avg(HospitalEvent.wait_time_minutes))\
        .filter(HospitalEvent.department == "ED").scalar() or 0

    # ICU specific
    icu_avg_wait = db.query(func.avg(HospitalEvent.wait_time_minutes))\
        .filter(HospitalEvent.department == "ICU").scalar() or 0

    # Lab turnaround
    lab_avg_wait = db.query(func.avg(HospitalEvent.wait_time_minutes))\
        .filter(HospitalEvent.department == "Lab").scalar() or 0

    # Transport delays
    transport_avg_wait = db.query(func.avg(HospitalEvent.wait_time_minutes))\
        .filter(HospitalEvent.department == "Transport").scalar() or 0

    # Discharge backlog — average wait for discharge events
    discharge_avg_wait = db.query(func.avg(HospitalEvent.wait_time_minutes))\
        .filter(HospitalEvent.event_type.in_(["discharge_started", "discharge_complete"]))\
        .scalar() or 0

    # High severity events in last 100 events
    recent_high_severity = db.query(HospitalEvent)\
        .filter(HospitalEvent.severity >= 4)\
        .order_by(HospitalEvent.id.desc())\
        .limit(100).count()

    return {
        "avg_wait_minutes": round(avg_wait, 1),
        "ed_avg_wait_minutes": round(ed_avg_wait, 1),
        "icu_avg_wait_minutes": round(icu_avg_wait, 1),
        "lab_avg_wait_minutes": round(lab_avg_wait, 1),
        "transport_avg_wait_minutes": round(transport_avg_wait, 1),
        "discharge_avg_wait_minutes": round(discharge_avg_wait, 1),
        "recent_high_severity_count": recent_high_severity,
    }


def detect_anomalies(metrics: dict) -> list:
    """Apply rule-based anomaly detection to current metrics."""
    alerts = []

    # --- ED wait time rules ---
    if metrics["ed_avg_wait_minutes"] > 90:
        alerts.append({
            "level": "critical",
            "department": "ED",
            "metric": "ed_avg_wait_minutes",
            "value": metrics["ed_avg_wait_minutes"],
            "message": f"ED average wait time is {metrics['ed_avg_wait_minutes']} min — critical threshold exceeded (>90 min)"
        })
    elif metrics["ed_avg_wait_minutes"] > 60:
        alerts.append({
            "level": "warning",
            "department": "ED",
            "metric": "ed_avg_wait_minutes",
            "value": metrics["ed_avg_wait_minutes"],
            "message": f"ED average wait time is {metrics['ed_avg_wait_minutes']} min — approaching critical threshold (>60 min)"
        })

    # --- ICU wait time rules ---
    if metrics["icu_avg_wait_minutes"] > 80:
        alerts.append({
            "level": "critical",
            "department": "ICU",
            "metric": "icu_avg_wait_minutes",
            "value": metrics["icu_avg_wait_minutes"],
            "message": f"ICU average wait is {metrics['icu_avg_wait_minutes']} min — possible capacity crisis"
        })
    elif metrics["icu_avg_wait_minutes"] > 50:
        alerts.append({
            "level": "warning",
            "department": "ICU",
            "metric": "icu_avg_wait_minutes",
            "value": metrics["icu_avg_wait_minutes"],
            "message": f"ICU average wait is {metrics['icu_avg_wait_minutes']} min — monitor closely"
        })

    # --- Lab turnaround rules ---
    if metrics["lab_avg_wait_minutes"] > 90:
        alerts.append({
            "level": "critical",
            "department": "Lab",
            "metric": "lab_avg_wait_minutes",
            "value": metrics["lab_avg_wait_minutes"],
            "message": f"Lab turnaround is {metrics['lab_avg_wait_minutes']} min — severe delay impacting patient flow"
        })
    elif metrics["lab_avg_wait_minutes"] > 60:
        alerts.append({
            "level": "warning",
            "department": "Lab",
            "metric": "lab_avg_wait_minutes",
            "value": metrics["lab_avg_wait_minutes"],
            "message": f"Lab turnaround is {metrics['lab_avg_wait_minutes']} min — delays likely affecting ED throughput"
        })

    # --- Discharge backlog rules ---
    if metrics["discharge_avg_wait_minutes"] > 75:
        alerts.append({
            "level": "critical",
            "department": "General Ward",
            "metric": "discharge_avg_wait_minutes",
            "value": metrics["discharge_avg_wait_minutes"],
            "message": f"Discharge average wait is {metrics['discharge_avg_wait_minutes']} min — backlog creating upstream ED pressure"
        })
    elif metrics["discharge_avg_wait_minutes"] > 50:
        alerts.append({
            "level": "warning",
            "department": "General Ward",
            "metric": "discharge_avg_wait_minutes",
            "value": metrics["discharge_avg_wait_minutes"],
            "message": f"Discharge average wait is {metrics['discharge_avg_wait_minutes']} min — monitor for backlog buildup"
        })

    # --- High severity event spike ---
    if metrics["recent_high_severity_count"] > 30:
        alerts.append({
            "level": "critical",
            "department": "Hospital-wide",
            "metric": "recent_high_severity_count",
            "value": metrics["recent_high_severity_count"],
            "message": f"{metrics['recent_high_severity_count']} high-severity events in last 100 — hospital under significant stress"
        })
    elif metrics["recent_high_severity_count"] > 20:
        alerts.append({
            "level": "warning",
            "department": "Hospital-wide",
            "metric": "recent_high_severity_count",
            "value": metrics["recent_high_severity_count"],
            "message": f"{metrics['recent_high_severity_count']} high-severity events in last 100 — elevated patient acuity"
        })

    if not alerts:
        alerts.append({
            "level": "ok",
            "department": "Hospital-wide",
            "metric": "all",
            "value": 0,
            "message": "All systems normal"
        })

    return alerts