import uuid
from datetime import datetime, timezone
from app import db


ACHIEVEMENT_TYPES = [
    ('streak', 'Streak'),
    ('total_completions', 'Total Completions'),
    ('days_sober', 'Days Sober'),
    ('journal', 'Journal Entries'),
    ('consistency', 'Consistency')
]


class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=True)
    achievement_type = db.Column(db.String(50), nullable=False)
    required_value = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Achievement name={self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'achievement_type': self.achievement_type,
            'required_value': self.required_value,
            'points': self.points
        }


class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    achievement_id = db.Column(db.String(36), db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    def __repr__(self):
        return f'<UserAchievement user_id={self.user_id} achievement_id={self.achievement_id}>'
