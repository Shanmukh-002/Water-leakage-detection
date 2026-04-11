from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Reading(db.Model):
    __tablename__ = "readings"
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.String(20), index=True, nullable=False)
    flow_lpm = db.Column(db.Float, nullable=False)
    pressure_kpa = db.Column(db.Float, nullable=True)
    ts = db.Column(db.DateTime, default=datetime.utcnow, index=True, nullable=False)

class LeakEvent(db.Model):
    __tablename__ = "leak_events"
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(50), index=True, nullable=False)   # node2->node3
    delta_lpm = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(20), nullable=False)              # INFO/WARNING/CRITICAL
    message = db.Column(db.String(200), nullable=False)
    ts = db.Column(db.DateTime, default=datetime.utcnow, index=True, nullable=False)
