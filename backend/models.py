from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from backend.database import Base

class HospitalEvent(Base):
    __tablename__ = "hospital_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String, index=True)
    department = Column(String)
    patient_id = Column(String)
    wait_time_minutes = Column(Float)
    severity = Column(Integer)
    scenario = Column(String)