from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app import db
from app.models import User, HabitLog, RelapseEvent
from datetime import datetime, timezone, timedelta

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/leaderboard')


@leaderboard_bp.route('/')
@login_required
def index():
    timeframe = request.args.get('timeframe', 'all')
    
    query = db.session.query(
        User.id,
        User.username,
        db.func.count(HabitLog.id).label('total_completions'),
        db.func.max(HabitLog.completed_at).label('last_completion')
    ).join(HabitLog, User.id == HabitLog.user_id)\
     .filter(User.is_active == True)\
     .group_by(User.id, User.username)
    
    if timeframe == 'week':
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        query = query.filter(HabitLog.completed_at >= week_ago)
    elif timeframe == 'month':
        month_ago = datetime.now(timezone.utc) - timedelta(days=30)
        query = query.filter(HabitLog.completed_at >= month_ago)
    
    completions_leaderboard = query.order_by(db.desc('total_completions')).limit(20).all()
    
    streak_query = db.session.query(
        User.id,
        User.username,
        db.func.count(HabitLog.id).label('streak_days')
    ).join(HabitLog, User.id == HabitLog.user_id)\
     .filter(User.is_active == True)\
     .filter(HabitLog.completed_at >= datetime.now(timezone.utc) - timedelta(days=30))\
     .group_by(User.id, User.username)\
     .order_by(db.desc('streak_days'))
    
    streak_leaderboard = streak_query.limit(20).all()
    
    sobriety_query = db.session.query(
        User.id,
        User.username,
        db.func.min(RelapseEvent.occurred_at).label('last_relapse'),
        db.func.count(RelapseEvent.id).label('relapse_count')
    ).join(RelapseEvent, User.id == RelapseEvent.user_id)\
     .filter(User.is_active == True)\
     .group_by(User.id, User.username)
    
    sobriety_data = sobriety_query.all()
    
    sobriety_leaderboard = []
    for user_id, username, last_relapse, relapse_count in sobriety_data:
        if last_relapse:
            days_sober = (datetime.now(timezone.utc) - last_relapse).days
        else:
            days_sober = 999
        sobriety_leaderboard.append({
            'user_id': user_id,
            'username': username,
            'days_sober': days_sober,
            'relapse_count': relapse_count
        })
    
    sobriety_leaderboard.sort(key=lambda x: (-x['days_sober'], x['relapse_count']))
    sobriety_leaderboard = sobriety_leaderboard[:20]
    
    points_query = User.query.filter_by(is_active=True).order_by(User.points.desc()).limit(20).all()
    points_leaderboard = [{'id': u.id, 'username': u.username, 'points': u.points} for u in points_query]
    
    user_rank_completions = None
    user_rank_streak = None
    user_rank_sobriety = None
    user_rank_points = None
    
    if current_user.is_authenticated:
        for i, entry in enumerate(completions_leaderboard):
            if entry.id == current_user.id:
                user_rank_completions = i + 1
                break
        
        for i, entry in enumerate(streak_leaderboard):
            if entry.id == current_user.id:
                user_rank_streak = i + 1
                break
        
        for i, entry in enumerate(sobriety_leaderboard):
            if entry['user_id'] == current_user.id:
                user_rank_sobriety = i + 1
                break
        
        for i, entry in enumerate(points_leaderboard):
            if entry['id'] == current_user.id:
                user_rank_points = i + 1
                break
    
    return render_template('leaderboard/index.html',
                          completions_leaderboard=completions_leaderboard,
                          streak_leaderboard=streak_leaderboard,
                          sobriety_leaderboard=sobriety_leaderboard,
                          points_leaderboard=points_leaderboard,
                          timeframe=timeframe,
                          user_rank_completions=user_rank_completions,
                          user_rank_streak=user_rank_streak,
                          user_rank_sobriety=user_rank_sobriety,
                          user_rank_points=user_rank_points)
