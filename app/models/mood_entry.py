import uuid
from datetime import datetime, timezone
from app import db


MOOD_CHOICES = [
    ('excellent', 'Excellent'),
    ('good', 'Good'),
    ('okay', 'Okay'),
    ('bad', 'Bad'),
    ('terrible', 'Terrible')
]


class MoodEntry(db.Model):
    __tablename__ = 'mood_entries'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    mood = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    triggers = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<MoodEntry user_id={self.user_id} date={self.date} mood={self.mood}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'mood': self.mood,
            'notes': self.notes,
            'triggers': self.triggers,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
