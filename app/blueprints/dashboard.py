from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.services import HabitService, RelapseService, StreakService
from datetime import datetime, timezone

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    habits = HabitService.get_user_habits(current_user.id)
    
    habit_summaries = []
    total_streak = 0
    
    for habit in habits:
        streak_info = StreakService.get_streak_info(habit)
        habit_summaries.append({
            'id': habit.id,
            'name': habit.name,
            'current_streak': streak_info['current'],
            'longest_streak': streak_info['longest'],
            'frequency': habit.frequency
        })
        total_streak += streak_info['current']
    
    today_completions = HabitService.get_user_completions_today(current_user.id)
    relapse_stats = RelapseService.get_relapse_stats(current_user.id)
    recent_relapses = RelapseService.get_user_relapses(current_user.id, limit=5)
    
    return render_template('dashboard/index.html',
                           habits=habit_summaries,
                           total_streak=total_streak,
                           today_completions=len(today_completions),
                           total_habits=len(habits),
                           relapse_stats=relapse_stats,
                           recent_relapses=recent_relapses)


@dashboard_bp.route('/overview')
@login_required
def overview():
    habits = HabitService.get_user_habits(current_user.id)
    
    total_current_streak = 0
    total_longest_streak = 0
    habit_counts = {'daily': 0, 'weekly': 0, 'monthly': 0}
    
    for habit in habits:
        streak_info = StreakService.get_streak_info(habit)
        total_current_streak += streak_info['current']
        total_longest_streak += streak_info['longest']
        habit_counts[habit.frequency] = habit_counts.get(habit.frequency, 0) + 1
    
    today_completions = HabitService.get_user_completions_today(current_user.id)
    relapse_stats = RelapseService.get_relapse_stats(current_user.id)
    
    return render_template('dashboard/overview.html',
                           total_current_streak=total_current_streak,
                           total_longest_streak=total_longest_streak,
                           habit_counts=habit_counts,
                           today_completions=today_completions,
                           relapse_stats=relapse_stats)
