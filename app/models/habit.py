import uuid
from datetime import datetime, timezone
from app import db

HABIT_CATEGORIES = [
    ('health', 'Health'),
    ('fitness', 'Fitness'),
    ('mental', 'Mental Health'),
    ('productivity', 'Productivity'),
    ('learning', 'Learning'),
    ('social', 'Social'),
    ('self_care', 'Self Care'),
    ('recovery', 'Recovery'),
    ('other', 'Other'),
]

HABIT_TEMPLATES = [
    {'name': 'Morning Meditation', 'description': '10 minutes of mindfulness meditation', 'category': 'mental'},
    {'name': 'Drink 8 Glasses of Water', 'description': 'Stay hydrated throughout the day', 'category': 'health'},
    {'name': 'Exercise for 30 Minutes', 'description': 'Physical activity to boost mood', 'category': 'fitness'},
    {'name': 'Read 10 Pages', 'description': 'Read a book or educational material', 'category': 'learning'},
    {'name': 'Journaling', 'description': 'Write about your day and feelings', 'category': 'mental'},
    {'name': 'Gratitude List', 'description': 'Write 3 things you are grateful for', 'category': 'mental'},
    {'name': 'Call a Friend', 'description': 'Connect with someone supportive', 'category': 'social'},
    {'name': 'Morning Walk', 'description': 'Start the day with fresh air', 'category': 'fitness'},
    {'name': 'No Social Media Before Noon', 'description': 'Avoid distractions in the morning', 'category': 'productivity'},
    {'name': 'Deep Breathing Exercise', 'description': '5 minutes of deep breathing', 'category': 'recovery'},
    {'name': 'Healthy Meal', 'description': 'Prepare a nutritious meal', 'category': 'health'},
    {'name': 'Bedtime at Same Time', 'description': 'Maintain consistent sleep schedule', 'category': 'health'},
    {'name': 'Practice Hobby', 'description': 'Spend time on something you enjoy', 'category': 'self_care'},
    {'name': 'Attend Support Meeting', 'description': 'Go to a recovery support group', 'category': 'recovery'},
    {'name': 'Stretching', 'description': '10 minutes of stretching', 'category': 'fitness'},
]


class Habit(db.Model):
    __tablename__ = 'habits'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    frequency = db.Column(db.String(20), nullable=False, default='daily')
    category = db.Column(db.String(50), nullable=True)
    reminder_time = db.Column(db.Time, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    logs = db.relationship('HabitLog', backref='habit', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Habit {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'frequency': self.frequency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def current_streak(self):
        from app.services.streak_service import StreakService
        return StreakService.calculate_current_streak(self)
    
    @property
    def longest_streak(self):
        from app.services.streak_service import StreakService
        return StreakService.calculate_longest_streak(self)
