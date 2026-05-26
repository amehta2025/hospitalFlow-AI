from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from backend.models import HospitalEvent


def compute_metrics(db: Session, window_minutes: int = 10) -> dict:
    cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)

    def avg_wait(department=None, event_types=None):
        q = db.query(func.avg(HospitalEvent.wait_time_minutes))\
            .filter(HospitalEvent.timestamp >= cutoff)
        if department:
            q = q.filter(HospitalEvent.department == department)
        if event_types:
            q = q.filter(HospitalEvent.event_type.in_(event_types))
        return round(q.scalar() or 0, 1)

    avg_wait_all = avg_wait()
    ed_avg = avg_wait(department="ED")
    icu_avg = avg_wait(department="ICU")
    lab_avg = avg_wait(department="Lab")
    transport_avg = avg_wait(department="Transport")
    discharge_avg = avg_wait(event_types=["discharge_started", "discharge_complete"])

    total_recent = db.query(HospitalEvent)\
        .filter(HospitalEvent.timestamp >= cutoff).count()

    high_severity_recent = db.query(HospitalEvent)\
        .filter(HospitalEvent.timestamp >= cutoff)\
        .filter(HospitalEvent.severity >= 4).count()

    high_severity_pct = round(
        (high_severity_recent / total_recent * 100) if total_recent > 0 else 0, 1
    )

    return {
        "window_minutes": window_minutes,
        "total_recent_events": total_recent,
        "avg_wait_minutes": avg_wait_all,
        "ed_avg_wait_minutes": ed_avg,
        "icu_avg_wait_minutes": icu_avg,
        "lab_avg_wait_minutes": lab_avg,
        "transport_avg_wait_minutes": transport_avg,
        "discharge_avg_wait_minutes": discharge_avg,
        "recent_high_severity_count": high_severity_recent,
        "recent_high_severity_pct": high_severity_pct,
    }


def detect_anomalies(metrics: dict) -> list:
    alerts = []

    if metrics["ed_avg_wait_minutes"] > 90:
        alerts.append({
            "level": "critical",
            "department": "ED",
            "metric": "ed_avg_wait_minutes",
            "value": metrics["ed_avg_wait_minutes"],
            "message": f"ED average wait is {metrics['ed_avg_wait_minutes']} min — critical threshold exceeded (>90 min)"
        })
    elif metrics["ed_avg_wait_minutes"] > 60:
        alerts.append({
            "level": "warning",
            "department": "ED",
            "metric": "ed_avg_wait_minutes",
            "value": metrics["ed_avg_wait_minutes"],
            "message": f"ED average wait is {metrics['ed_avg_wait_minutes']} min — approaching critical threshold (>60 min)"
        })

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

    if metrics["recent_high_severity_pct"] > 50:
        alerts.append({
            "level": "critical",
            "department": "Hospital-wide",
            "metric": "recent_high_severity_pct",
            "value": metrics["recent_high_severity_pct"],
            "message": f"{metrics['recent_high_severity_pct']}% of recent events are high-severity — hospital under significant stress"
        })
    elif metrics["recent_high_severity_pct"] > 35:
        alerts.append({
            "level": "warning",
            "department": "Hospital-wide",
            "metric": "recent_high_severity_pct",
            "value": metrics["recent_high_severity_pct"],
            "message": f"{metrics['recent_high_severity_pct']}% of recent events are high-severity — elevated patient acuity"
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