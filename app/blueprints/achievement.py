from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services import AchievementService, HabitService, JournalService
from app.models import UserAchievement

achievement_bp = Blueprint('achievement', __name__, url_prefix='/achievements')


@achievement_bp.route('/')
@login_required
def index():
    all_achievements = AchievementService.get_all_achievements()
    user_achievements = AchievementService.get_user_achievements(current_user.id)
    earned_ids = {ua.achievement_id for ua in user_achievements}
    user_points = AchievementService.get_user_points(current_user.id)
    
    habits = HabitService.get_user_habits(current_user.id)
    total_completions = HabitService.get_total_completions(current_user.id)
    journal_count = JournalService.get_entry_count(current_user.id)
    
    return render_template('achievement/index.html',
                           achievements=all_achievements,
                           user_achievements=user_achievements,
                           earned_ids=earned_ids,
                           user_points=user_points,
                           total_completions=total_completions,
                           journal_count=journal_count)


@achievement_bp.route('/init', methods=['POST'])
@login_required
def init():
    if current_user.is_admin:
        achievements = AchievementService.initialize_default_achievements()
        flash(f'Initialized {len(achievements)} default achievements', 'success')
    return redirect(url_for('achievement.index'))
