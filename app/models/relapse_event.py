import uuid
from datetime import datetime, timezone
from app import db


TRIGGER_TYPES = [
    'emotional_distress',
    'social_situation', 
    'environmental_cue',
    'stress',
    'peer_pressure',
    'other'
]


class RelapseEvent(db.Model):
    __tablename__ = 'relapse_events'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    occurred_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    trigger_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<RelapseEvent user_id={self.user_id} occurred_at={self.occurred_at}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'occurred_at': self.occurred_at.isoformat() if self.occurred_at else None,
            'trigger_type': self.trigger_type,
            'severity': self.severity,
            'notes': self.notes
        }
    
    @staticmethod
    def validate_trigger_type(value):
        return value in TRIGGER_TYPES
    
    @staticmethod
    def validate_severity(value):
        return 1 <= value <= 10
