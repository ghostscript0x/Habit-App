from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from app.services import ExportService, HabitService, StreakService
from datetime import date, timedelta
import calendar

export_bp = Blueprint('export', __name__, url_prefix='/export')


@export_bp.route('/')
@login_required
def index():
    stats = ExportService.get_stats_summary(current_user.id)
    return render_template('export/index.html', stats=stats)


@export_bp.route('/habits')
@login_required
def export_habits():
    csv_data = ExportService.export_habits_csv(current_user.id)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=habits_{date.today()}.csv'
    return response


@export_bp.route('/logs')
@login_required
def export_logs():
    csv_data = ExportService.export_habit_logs_csv(current_user.id)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=habit_logs_{date.today()}.csv'
    return response


@export_bp.route('/relapses')
@login_required
def export_relapses():
    csv_data = ExportService.export_relapses_csv(current_user.id)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=relapses_{date.today()}.csv'
    return response


@export_bp.route('/journal')
@login_required
def export_journal():
    csv_data = ExportService.export_journal_csv(current_user.id)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=journal_{date.today()}.csv'
    return response


@export_bp.route('/mood')
@login_required
def export_mood():
    csv_data = ExportService.export_mood_csv(current_user.id)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=mood_{date.today()}.csv'
    return response


@export_bp.route('/all')
@login_required
def export_all():
    csv_data = ExportService.export_all_data(current_user.id)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=all_data_{date.today()}.csv'
    return response


calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')


@calendar_bp.route('/')
@login_required
def index():
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)
    
    habits = HabitService.get_user_habits(current_user.id)
    
    from datetime import datetime
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()
    
    habit_data = []
    for habit in habits:
        logs = HabitService.get_completions_by_date_range(
            current_user.id, habit.id, start_date, end_date
        )
        log_dates = {log.completed_at.date() for log in logs}
        
        streak_info = StreakService.get_streak_info(habit)
        
        habit_data.append({
            'id': habit.id,
            'name': habit.name,
            'dates': log_dates,
            'current_streak': streak_info['current']
        })
    
    month_calendar = calendar.Calendar().monthdayscalendar(year, month)
    month_name = calendar.month_name[month]
    
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    return render_template('calendar/index.html',
                           year=year,
                           month=month,
                           month_name=month_name,
                           month_calendar=month_calendar,
                           habit_data=habit_data,
                           habits=habits,
                           prev_month=prev_month,
                           prev_year=prev_year,
                           next_month=next_month,
                           next_year=next_year,
                           today=date.today())
