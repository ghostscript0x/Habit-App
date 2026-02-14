import uuid
from datetime import datetime, timezone
from app import db


class ConsistencyBuilder(db.Model):
    __tablename__ = 'consistency_builders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    target_frequency = db.Column(db.Integer, nullable=False, default=1)
    current_count = db.Column(db.Integer, default=0)
    best_count = db.Column(db.Integer, default=0)
    streak_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    started_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_completed = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<ConsistencyBuilder user_id={self.user_id} name={self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'target_frequency': self.target_frequency,
            'current_count': self.current_count,
            'best_count': self.best_count,
            'streak_count': self.streak_count,
            'is_active': self.is_active,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'last_completed': self.last_completed.isoformat() if self.last_completed else None
        }
