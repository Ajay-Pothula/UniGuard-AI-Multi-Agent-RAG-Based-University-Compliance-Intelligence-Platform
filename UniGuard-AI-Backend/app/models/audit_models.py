"""
app/models/audit_models.py
--------------------------
SQLAlchemy models for Audit Logging to SQLite.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_role = Column(String(50), index=True)
    query = Column(Text)
    intent = Column(String(100)) # Decided by Classifier Agent
    risk_level = Column(String(50)) # Decided by Compliance Agent
    confidence_score = Column(String(10)) 
    decision_summary = Column(Text)
    needs_review = Column(Integer, default=0) # boolean via integer 0/1
