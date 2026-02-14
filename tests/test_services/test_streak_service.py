import pytest
from datetime import datetime, timezone, timedelta
from app.services import StreakService
from app.models import HabitLog
from app import db


class TestStreakService:
    
    def test_calculate_current_streak_no_logs(self, app, test_habit):
        streak = StreakService.calculate_current_streak(test_habit)
        assert streak == 0
    
    def test_calculate_current_streak_single_log(self, app, test_user, test_habit):
        log = HabitLog(
            habit_id=test_habit.id,
            user_id=test_user.id,
            completed_at=datetime.now(timezone.utc),
            streak_count=1
        )
        db.session.add(log)
        db.session.commit()
        
        streak = StreakService.calculate_current_streak(test_habit)
        assert streak == 1
    
    def test_calculate_current_streak_consecutive_days(self, app, test_user, test_habit):
        today = datetime.now(timezone.utc)
        
        for i in range(3):
            log = HabitLog(
                habit_id=test_habit.id,
                user_id=test_user.id,
                completed_at=today - timedelta(days=i),
                streak_count=i + 1
            )
            db.session.add(log)
        db.session.commit()
        
        streak = StreakService.calculate_current_streak(test_habit)
        assert streak == 3
    
    def test_calculate_longest_streak(self, app, test_user, test_habit):
        dates = [
            datetime.now(timezone.utc) - timedelta(days=i * 2)
            for i in range(5)
        ]
        
        for i, date in enumerate(dates):
            log = HabitLog(
                habit_id=test_habit.id,
                user_id=test_user.id,
                completed_at=date,
                streak_count=1
            )
            db.session.add(log)
        db.session.commit()
        
        longest = StreakService.calculate_longest_streak(test_habit)
        assert longest >= 1
    
    def test_get_streak_info(self, app, test_user, test_habit):
        log = HabitLog(
            habit_id=test_habit.id,
            user_id=test_user.id,
            completed_at=datetime.now(timezone.utc),
            streak_count=5
        )
        db.session.add(log)
        db.session.commit()
        
        info = StreakService.get_streak_info(test_habit)
        
        assert 'current' in info
        assert 'longest' in info
