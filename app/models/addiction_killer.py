import uuid
from datetime import datetime, timezone
from app import db


CRAFTING_TECHNIQUES = [
    ('deep_breathing', 'Deep Breathing'),
    ('progressive_muscle', 'Progressive Muscle Relaxation'),
    ('mindfulness', 'Mindfulness Meditation'),
    ('urge Surfing', 'Urge Surfing'),
    ('cognitive_reframing', 'Cognitive Reframing'),
    ('physical_activity', 'Physical Activity'),
    ('gratitude_practice', 'Gratitude Practice'),
    ('connection', 'Social Connection'),
    ('journaling', 'Urge Journaling'),
    ('visualization', 'Visualization')
]


class AddictionKiller(db.Model):
    __tablename__ = 'addiction_killers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    target_addiction = db.Column(db.String(100), nullable=True)
    technique = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    times_used = db.Column(db.Integer, default=0)
    effectiveness_rating = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<AddictionKiller user_id={self.user_id} name={self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'target_addiction': self.target_addiction,
            'technique': self.technique,
            'notes': self.notes,
            'times_used': self.times_used,
            'effectiveness_rating': self.effectiveness_rating,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AddictionSession(db.Model):
    __tablename__ = 'addiction_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    killer_id = db.Column(db.String(36), db.ForeignKey('addiction_killers.id'), nullable=False)
    craving_intensity = db.Column(db.Integer, nullable=False)
    after_intensity = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    killer = db.relationship('AddictionKiller', backref='sessions')
    
    def __repr__(self):
        return f'<AddictionSession user_id={self.user_id} killer_id={self.killer_id}>'
