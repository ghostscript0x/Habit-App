from datetime import datetime, date, timezone
from app import db
from app.models import JournalEntry


class JournalService:
    
    @staticmethod
    def create_entry(user_id, content, mood=None, tags=None, entry_date=None):
        entry = JournalEntry(
            user_id=user_id,
            content=content,
            mood=mood,
            tags=tags,
            date=entry_date or date.today()
        )
        db.session.add(entry)
        db.session.commit()
        return entry
    
    @staticmethod
    def get_entry(user_id, entry_id):
        return JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    
    @staticmethod
    def get_user_entries(user_id, limit=50, offset=0):
        return JournalEntry.query.filter_by(user_id=user_id)\
            .order_by(JournalEntry.date.desc(), JournalEntry.created_at.desc())\
            .limit(limit).offset(offset).all()
    
    @staticmethod
    def get_entries_by_date(user_id, entry_date):
        return JournalEntry.query.filter_by(user_id=user_id, date=entry_date).all()
    
    @staticmethod
    def get_entries_by_mood(user_id, mood):
        return JournalEntry.query.filter_by(user_id=user_id, mood=mood)\
            .order_by(JournalEntry.date.desc()).all()
    
    @staticmethod
    def update_entry(entry_id, user_id, **kwargs):
        entry = JournalService.get_entry(user_id, entry_id)
        if not entry:
            return None
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        entry.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return entry
    
    @staticmethod
    def delete_entry(entry_id, user_id):
        entry = JournalService.get_entry(user_id, entry_id)
        if not entry:
            return False
        db.session.delete(entry)
        db.session.commit()
        return True
    
    @staticmethod
    def get_entry_count(user_id):
        return JournalEntry.query.filter_by(user_id=user_id).count()
    
    @staticmethod
    def get_recent_entries_with_limit(user_id, days=7):
        from datetime import timedelta
        start_date = date.today() - timedelta(days=days)
        return JournalEntry.query.filter(
            JournalEntry.user_id == user_id,
            JournalEntry.date >= start_date
        ).order_by(JournalEntry.date.desc()).all()
