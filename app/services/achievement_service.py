from datetime import datetime, timezone
from app import db
from app.models import Achievement, UserAchievement


class AchievementService:
    
    @staticmethod
    def create_achievement(name, description, achievement_type, required_value, icon=None, points=0):
        achievement = Achievement(
            name=name,
            description=description,
            achievement_type=achievement_type,
            required_value=required_value,
            icon=icon,
            points=points
        )
        db.session.add(achievement)
        db.session.commit()
        return achievement
    
    @staticmethod
    def get_achievement(achievement_id):
        return Achievement.query.get(achievement_id)
    
    @staticmethod
    def get_all_achievements():
        return Achievement.query.all()
    
    @staticmethod
    def get_achievements_by_type(achievement_type):
        return Achievement.query.filter_by(achievement_type=achievement_type).all()
    
    @staticmethod
    def award_achievement(user_id, achievement_id):
        existing = UserAchievement.query.filter_by(
            user_id=user_id, 
            achievement_id=achievement_id
        ).first()
        if existing:
            return None
        
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id
        )
        db.session.add(user_achievement)
        db.session.commit()
        return user_achievement
    
    @staticmethod
    def get_user_achievements(user_id):
        return UserAchievement.query.filter_by(user_id=user_id)\
            .order_by(UserAchievement.earned_at.desc()).all()
    
    @staticmethod
    def has_achievement(user_id, achievement_id):
        return UserAchievement.query.filter_by(
            user_id=user_id, 
            achievement_id=achievement_id
        ).first() is not None
    
    @staticmethod
    def check_and_award_streak_achievements(user_id, streak_count):
        achievements = Achievement.query.filter_by(achievement_type='streak').all()
        awarded = []
        for achievement in achievements:
            if streak_count >= achievement.required_value:
                if not AchievementService.has_achievement(user_id, achievement.id):
                    AchievementService.award_achievement(user_id, achievement.id)
                    awarded.append(achievement)
        return awarded
    
    @staticmethod
    def check_and_award_completion_achievements(user_id, total_completions):
        achievements = Achievement.query.filter_by(achievement_type='total_completions').all()
        awarded = []
        for achievement in achievements:
            if total_completions >= achievement.required_value:
                if not AchievementService.has_achievement(user_id, achievement.id):
                    AchievementService.award_achievement(user_id, achievement.id)
                    awarded.append(achievement)
        return awarded
    
    @staticmethod
    def get_user_points(user_id):
        achievements = AchievementService.get_user_achievements(user_id)
        return sum(ua.achievement.points for ua in achievements)
    
    @staticmethod
    def initialize_default_achievements():
        defaults = [
            ('7 Day Streak', 'Maintain a 7-day streak', 'streak', 7, 'bi-fire', 10),
            ('30 Day Streak', 'Maintain a 30-day streak', 'streak', 30, 'bi-fire', 50),
            ('90 Day Streak', 'Maintain a 90-day streak', 'streak', 90, 'bi-trophy', 100),
            ('180 Day Streak', 'Maintain a 180-day streak', 'streak', 180, 'bi-award', 200),
            ('365 Day Streak', 'Maintain a 365-day streak', 'streak', 365, 'bi-gem', 500),
            ('First Steps', 'Complete your first habit', 'total_completions', 1, 'bi-star', 5),
            ('10 Completions', 'Complete 10 habits', 'total_completions', 10, 'bi-star-fill', 15),
            ('50 Completions', 'Complete 50 habits', 'total_completions', 50, 'bi-stars', 30),
            ('100 Completions', 'Complete 100 habits', 'total_completions', 100, 'bi-patch-check', 50),
            ('500 Completions', 'Complete 500 habits', 'total_completions', 500, 'bi-patch-check-fill', 100),
            ('First Journal', 'Write your first journal entry', 'journal', 1, 'bi-journal-text', 5),
            ('10 Journals', 'Write 10 journal entries', 'journal', 10, 'bi-journal-richtext', 20),
            ('30 Day Journaler', 'Write 30 journal entries', 'journal', 30, 'bi-book', 50),
        ]
        
        for name, desc, atype, value, icon, points in defaults:
            existing = Achievement.query.filter_by(name=name).first()
            if not existing:
                AchievementService.create_achievement(name, desc, atype, value, icon, points)
        
        return Achievement.query.all()
