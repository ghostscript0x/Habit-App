from datetime import datetime, timezone
from app import db
from app.models import Habit, HabitLog


class HabitService:
    
    @staticmethod
    def create_habit(user_id, name, description=None, frequency='daily'):
        habit = Habit(
            user_id=user_id,
            name=name,
            description=description,
            frequency=frequency
        )
        
        db.session.add(habit)
        db.session.commit()
        
        return habit
    
    @staticmethod
    def get_habit_by_id(habit_id):
        return Habit.query.get(habit_id)
    
    @staticmethod
    def get_user_habits(user_id, active_only=True):
        query = Habit.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Habit.created_at.desc()).all()
    
    @staticmethod
    def update_habit(habit_id, **kwargs):
        habit = Habit.query.get(habit_id)
        if not habit:
            return None
        
        allowed_fields = ['name', 'description', 'frequency', 'is_active']
        for field in allowed_fields:
            if field in kwargs:
                setattr(habit, field, kwargs[field])
        
        habit.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return habit
    
    @staticmethod
    def delete_habit(habit_id):
        habit = Habit.query.get(habit_id)
        if not habit:
            return False
        
        db.session.delete(habit)
        db.session.commit()
        
        return True
    
    @staticmethod
    def complete_habit(habit_id, user_id, notes=None):
        habit = Habit.query.get(habit_id)
        if not habit or habit.user_id != user_id:
            return None
        
        from app.services.streak_service import StreakService
        streak_count = StreakService.calculate_current_streak(habit) + 1
        
        log = HabitLog(
            habit_id=habit_id,
            user_id=user_id,
            completed_at=datetime.now(timezone.utc),
            streak_count=streak_count,
            notes=notes
        )
        
        db.session.add(log)
        db.session.commit()
        
        return log
    
    @staticmethod
    def get_habit_logs(habit_id, limit=None):
        query = HabitLog.query.filter_by(habit_id=habit_id).order_by(HabitLog.completed_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_user_completions_today(user_id):
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        return HabitLog.query.filter(
            HabitLog.user_id == user_id,
            HabitLog.completed_at >= today_start
        ).all()
    
    @staticmethod
    def get_total_completions(user_id):
        return HabitLog.query.filter_by(user_id=user_id).count()
