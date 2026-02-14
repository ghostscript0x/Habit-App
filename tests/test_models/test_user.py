import pytest
from app.models import User, Habit, HabitLog, RelapseEvent
from app import db


class TestUserModel:
    
    def test_create_user(self, app):
        from app.services import AuthService
        user = AuthService.create_user(
            email='new@example.com',
            username='newuser',
            password='password123'
        )
        
        assert user.email == 'new@example.com'
        assert user.username == 'newuser'
        assert user.is_active is True
        assert user.is_admin is False
    
    def test_duplicate_email(self, app, test_user):
        from app.services import AuthService
        with pytest.raises(ValueError):
            AuthService.create_user(
                email='test@example.com',
                username='different',
                password='password123'
            )
    
    def test_duplicate_username(self, app, test_user):
        from app.services import AuthService
        with pytest.raises(ValueError):
            AuthService.create_user(
                email='different@example.com',
                username='testuser',
                password='password123'
            )


class TestHabitModel:
    
    def test_create_habit(self, app, test_user):
        from app.services import HabitService
        habit = HabitService.create_habit(
            user_id=test_user.id,
            name='Meditation',
            description='Daily meditation',
            frequency='daily'
        )
        
        assert habit.name == 'Meditation'
        assert habit.frequency == 'daily'
        assert habit.is_active is True
    
    def test_get_user_habits(self, app, test_user, test_habit):
        from app.services import HabitService
        habits = HabitService.get_user_habits(test_user.id)
        
        assert len(habits) == 1
        assert habits[0].name == 'Exercise'


class TestHabitLogModel:
    
    def test_complete_habit(self, app, test_user, test_habit):
        from app.services import HabitService
        log = HabitService.complete_habit(test_habit.id, test_user.id)
        
        assert log is not None
        assert log.habit_id == test_habit.id
        assert log.user_id == test_user.id
        assert log.streak_count == 1
    
    def test_streak_increments(self, app, test_user, test_habit):
        from app.services import HabitService
        from datetime import datetime, timezone, timedelta
        
        HabitService.complete_habit(test_habit.id, test_user.id)
        
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        log2 = HabitLog(
            habit_id=test_habit.id,
            user_id=test_user.id,
            completed_at=yesterday,
            streak_count=1
        )
        db.session.add(log2)
        db.session.commit()
        
        log3 = HabitService.complete_habit(test_habit.id, test_user.id)
        assert log3.streak_count == 2


class TestRelapseEventModel:
    
    def test_create_relapse(self, app, test_user):
        from app.services import RelapseService
        relapse = RelapseService.create_relapse(
            user_id=test_user.id,
            occurred_at=None,
            trigger_type='stress',
            severity=5,
            notes='Had a hard day'
        )
        
        assert relapse.trigger_type == 'stress'
        assert relapse.severity == 5
    
    def test_invalid_trigger_type(self, app, test_user):
        from app.services import RelapseService
        with pytest.raises(ValueError):
            RelapseService.create_relapse(
                user_id=test_user.id,
                occurred_at=None,
                trigger_type='invalid_type',
                severity=5
            )
    
    def test_invalid_severity(self, app, test_user):
        from app.services import RelapseService
        with pytest.raises(ValueError):
            RelapseService.create_relapse(
                user_id=test_user.id,
                occurred_at=None,
                trigger_type='stress',
                severity=15
            )
    
    def test_get_relapse_stats(self, app, test_user):
        from app.services import RelapseService
        RelapseService.create_relapse(
            user_id=test_user.id,
            occurred_at=None,
            trigger_type='stress',
            severity=5
        )
        RelapseService.create_relapse(
            user_id=test_user.id,
            occurred_at=None,
            trigger_type='stress',
            severity=7
        )
        
        stats = RelapseService.get_relapse_stats(test_user.id)
        
        assert stats['total_count'] == 2
        assert stats['avg_severity'] == 6.0
        assert stats['trigger_breakdown']['stress'] == 2
