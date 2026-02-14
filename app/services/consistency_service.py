from datetime import datetime, timezone, timedelta
from app import db
from app.models import ConsistencyBuilder


class ConsistencyService:
    
    @staticmethod
    def create_builder(user_id, name, description=None, target_frequency=1):
        builder = ConsistencyBuilder(
            user_id=user_id,
            name=name,
            description=description,
            target_frequency=target_frequency
        )
        db.session.add(builder)
        db.session.commit()
        return builder
    
    @staticmethod
    def get_builder(user_id, builder_id):
        return ConsistencyBuilder.query.filter_by(id=builder_id, user_id=user_id).first()
    
    @staticmethod
    def get_user_builders(user_id, active_only=True):
        query = ConsistencyBuilder.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(ConsistencyBuilder.created_at.desc()).all()
    
    @staticmethod
    def increment_completion(user_id, builder_id):
        builder = ConsistencyService.get_builder(user_id, builder_id)
        if not builder:
            return None
        
        now = datetime.now(timezone.utc)
        
        if builder.last_completed:
            days_since = (now - builder.last_completed).days
            if days_since == 1:
                builder.streak_count += 1
            elif days_since > 1:
                builder.streak_count = 1
        else:
            builder.streak_count = 1
        
        builder.current_count += 1
        builder.last_completed = now
        
        if builder.current_count > builder.best_count:
            builder.best_count = builder.current_count
        
        db.session.commit()
        return builder
    
    @staticmethod
    def update_builder(builder_id, user_id, **kwargs):
        builder = ConsistencyService.get_builder(user_id, builder_id)
        if not builder:
            return None
        for key, value in kwargs.items():
            if hasattr(builder, key):
                setattr(builder, key, value)
        db.session.commit()
        return builder
    
    @staticmethod
    def delete_builder(builder_id, user_id):
        builder = ConsistencyService.get_builder(user_id, builder_id)
        if not builder:
            return False
        db.session.delete(builder)
        db.session.commit()
        return True
    
    @staticmethod
    def reset_streak(user_id, builder_id):
        builder = ConsistencyService.get_builder(user_id, builder_id)
        if builder:
            builder.streak_count = 0
            builder.current_count = 0
            db.session.commit()
        return builder
    
    @staticmethod
    def get_active_builders(user_id):
        return ConsistencyBuilder.query.filter_by(user_id=user_id, is_active=True).all()
    
    @staticmethod
    def get_streak_leaders(user_id, limit=5):
        return ConsistencyBuilder.query.filter_by(user_id=user_id)\
            .order_by(ConsistencyBuilder.streak_count.desc()).limit(limit).all()
    
    @staticmethod
    def get_builder_stats(user_id):
        builders = ConsistencyService.get_user_builders(user_id, active_only=False)
        return {
            'total': len(builders),
            'active': sum(1 for b in builders if b.is_active),
            'total_completions': sum(b.current_count for b in builders),
            'best_streak': max((b.streak_count for b in builders), default=0)
        }
