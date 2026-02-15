from datetime import datetime, timezone
from app import db
from app.models import Trigger


class TriggerService:
    
    @staticmethod
    def create_trigger(user_id, name, description=None, category=None):
        trigger = Trigger(
            user_id=user_id,
            name=name,
            description=description,
            category=category
        )
        db.session.add(trigger)
        db.session.commit()
        return trigger
    
    @staticmethod
    def get_trigger(user_id, trigger_id):
        return Trigger.query.filter_by(id=trigger_id, user_id=user_id).first()
    
    @staticmethod
    def get_user_triggers(user_id, active_only=True):
        query = Trigger.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Trigger.name.asc()).all()
    
    @staticmethod
    def get_triggers_by_category(user_id, category):
        return Trigger.query.filter_by(user_id=user_id, category=category)\
            .order_by(Trigger.name.asc()).all()
    
    @staticmethod
    def update_trigger(trigger_id, user_id, **kwargs):
        trigger = TriggerService.get_trigger(user_id, trigger_id)
        if not trigger:
            return None
        for key, value in kwargs.items():
            if hasattr(trigger, key):
                setattr(trigger, key, value)
        trigger.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return trigger
    
    @staticmethod
    def delete_trigger(trigger_id, user_id):
        trigger = TriggerService.get_trigger(user_id, trigger_id)
        if not trigger:
            return False
        db.session.delete(trigger)
        db.session.commit()
        return True
    
    @staticmethod
    def increment_encountered(trigger_id, user_id):
        trigger = TriggerService.get_trigger(user_id, trigger_id)
        if trigger:
            trigger.times_encountered += 1
            db.session.commit()
        return trigger
    
    @staticmethod
    def increment_overcome(trigger_id, user_id):
        trigger = TriggerService.get_trigger(user_id, trigger_id)
        if trigger:
            trigger.times_overcome += 1
            db.session.commit()
        return trigger
    
    @staticmethod
    def get_most_encountered(user_id, limit=5):
        return Trigger.query.filter_by(user_id=user_id)\
            .order_by(Trigger.times_encountered.desc()).limit(limit).all()
    
    @staticmethod
    def get_most_overcome(user_id, limit=5):
        return Trigger.query.filter_by(user_id=user_id)\
            .order_by(Trigger.times_overcome.desc()).limit(limit).all()
    
    @staticmethod
    def get_trigger_stats(user_id):
        triggers = TriggerService.get_user_triggers(user_id, active_only=False)
        return {
            'total': len(triggers),
            'active': sum(1 for t in triggers if t.is_active),
            'total_encountered': sum(t.times_encountered or 0 for t in triggers),
            'total_overcome': sum(t.times_overcome or 0 for t in triggers)
        }
