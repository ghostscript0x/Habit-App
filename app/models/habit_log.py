import uuid
from datetime import datetime, timezone
from app import db


class HabitLog(db.Model):
    __tablename__ = 'habit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    habit_id = db.Column(db.String(36), db.ForeignKey('habits.id'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    streak_count = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<HabitLog habit_id={self.habit_id} completed_at={self.completed_at}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'habit_id': self.habit_id,
            'user_id': self.user_id,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'streak_count': self.streak_count,
            'notes': self.notes
        }
