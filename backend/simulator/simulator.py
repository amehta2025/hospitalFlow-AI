import random
import requests
import time
import json
import os
from datetime import datetime

# --- Config ---
SCENARIO = "normal"  # options: "normal", "surge", "lab_delay", "icu_full"

EVENT_TYPES = [
    "patient_arrival",
    "triage_complete",
    "bed_assigned",
    "lab_ordered",
    "lab_result_returned",
    "transport_requested",
    "transport_complete",
    "discharge_started",
    "discharge_complete",
    "icu_bed_available",
    "nurse_staffing_update",
]

DEPARTMENTS = ["ED", "ICU", "Radiology", "Lab", "General Ward", "Transport"]

def get_wait_time(event_type: str) -> int:
    """Return a realistic wait time in minutes based on scenario and event type."""
    base_times = {
        "patient_arrival": 0,
        "triage_complete": random.randint(5, 20),
        "bed_assigned": random.randint(10, 40),
        "lab_ordered": random.randint(2, 10),
        "lab_result_returned": random.randint(30, 90),
        "transport_requested": random.randint(5, 20),
        "transport_complete": random.randint(10, 30),
        "discharge_started": random.randint(20, 60),
        "discharge_complete": random.randint(30, 90),
        "icu_bed_available": random.randint(0, 5),
        "nurse_staffing_update": 0,
    }

    wait = base_times.get(event_type, 10)

    # Modify wait times based on scenario
    if SCENARIO == "surge":
        wait = int(wait * random.uniform(1.5, 2.5))
    elif SCENARIO == "lab_delay":
        if "lab" in event_type:
            wait = int(wait * random.uniform(2.0, 3.5))
    elif SCENARIO == "icu_full":
        if event_type in ["bed_assigned", "discharge_started"]:
            wait = int(wait * random.uniform(2.0, 3.0))

    return wait


def generate_event(patient_id: int) -> dict:
    """Generate a single random hospital event."""
    event_type = random.choice(EVENT_TYPES)
    department = random.choice(DEPARTMENTS)
    severity = random.randint(1, 5)
    wait_time = get_wait_time(event_type)

    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "department": department,
        "patient_id": f"P{patient_id:04d}",
        "wait_time_minutes": wait_time,
        "severity": severity,
        "scenario": SCENARIO,
    }

    return event


def run_simulator(interval_seconds: float = 1.0, num_events: int = None):
    """Stream hospital events to the FastAPI backend."""
    print(f"Starting HospitalFlow simulator — scenario: {SCENARIO}")
    print("-" * 50)

    patient_counter = 1000
    events_generated = 0

    try:
        while True:
            if random.random() < 0.3:
                patient_counter += 1

            event = generate_event(patient_counter)
            
            # Send to API instead of just printing
            try:
                response = requests.post(f"http://127.0.0.1:{os.getenv('PORT', '8000')}/events", json=event)
                print(f"Sent: {event['event_type']} | {event['department']} | wait: {event['wait_time_minutes']}min | status: {response.status_code}")
            except Exception as e:
                print(f"Failed to send event: {e}")

            events_generated += 1
            if num_events and events_generated >= num_events:
                break

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")