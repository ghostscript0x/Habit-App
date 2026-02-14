from datetime import datetime, date, timezone
from app import db
from app.models import MoodEntry


class MoodService:
    
    @staticmethod
    def create_entry(user_id, mood, notes=None, triggers=None, entry_date=None):
        entry = MoodEntry(
            user_id=user_id,
            mood=mood,
            notes=notes,
            triggers=triggers,
            date=entry_date or date.today()
        )
        db.session.add(entry)
        db.session.commit()
        return entry
    
    @staticmethod
    def get_entry(user_id, entry_id):
        return MoodEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    
    @staticmethod
    def get_today_entry(user_id):
        return MoodEntry.query.filter_by(user_id=user_id, date=date.today()).first()
    
    @staticmethod
    def get_user_entries(user_id, limit=50):
        return MoodEntry.query.filter_by(user_id=user_id)\
            .order_by(MoodEntry.date.desc()).limit(limit).all()
    
    @staticmethod
    def get_entries_by_date_range(user_id, start_date, end_date):
        return MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            MoodEntry.date >= start_date,
            MoodEntry.date <= end_date
        ).order_by(MoodEntry.date.desc()).all()
    
    @staticmethod
    def get_mood_trend(user_id, days=30):
        from datetime import timedelta
        start_date = date.today() - timedelta(days=days)
        entries = MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            MoodEntry.date >= start_date
        ).order_by(MoodEntry.date.asc()).all()
        
        mood_values = {'excellent': 5, 'good': 4, 'okay': 3, 'bad': 2, 'terrible': 1}
        return [
            {'date': e.date, 'mood': e.mood, 'value': mood_values.get(e.mood, 3)}
            for e in entries
        ]
    
    @staticmethod
    def get_average_mood(user_id, days=30):
        trend = MoodService.get_mood_trend(user_id, days)
        if not trend:
            return None
        return sum(t['value'] for t in trend) / len(trend)
    
    @staticmethod
    def update_entry(entry_id, user_id, **kwargs):
        entry = MoodService.get_entry(user_id, entry_id)
        if not entry:
            return None
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        db.session.commit()
        return entry
    
    @staticmethod
    def delete_entry(entry_id, user_id):
        entry = MoodService.get_entry(user_id, entry_id)
        if not entry:
            return False
        db.session.delete(entry)
        db.session.commit()
        return True
    
    @staticmethod
    def get_mood_distribution(user_id, days=30):
        from datetime import timedelta
        start_date = date.today() - timedelta(days=days)
        entries = MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            MoodEntry.date >= start_date
        ).all()
        
        distribution = {}
        for entry in entries:
            distribution[entry.mood] = distribution.get(entry.mood, 0) + 1
        return distribution
