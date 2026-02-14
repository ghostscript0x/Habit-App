from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Habit, HabitLog, RelapseEvent
from app.services import AuthService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def index():
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_habits = Habit.query.count()
    total_completions = HabitLog.query.count()
    total_relapses = RelapseEvent.query.count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template('admin/index.html',
                           total_users=total_users,
                           active_users=active_users,
                           total_habits=total_habits,
                           total_completions=total_completions,
                           total_relapses=total_relapses,
                           recent_users=recent_users)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=pagination.items, pagination=pagination)


@admin_bp.route('/users/<user_id>')
@login_required
@admin_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    
    habits = Habit.query.filter_by(user_id=user_id).all()
    habit_logs = HabitLog.query.filter_by(user_id=user_id).order_by(HabitLog.completed_at.desc()).limit(50).all()
    relapses = RelapseEvent.query.filter_by(user_id=user_id).order_by(RelapseEvent.occurred_at.desc()).limit(50).all()
    
    total_habits = len(habits)
    total_completions = HabitLog.query.filter_by(user_id=user_id).count()
    total_relapses = RelapseEvent.query.filter_by(user_id=user_id).count()
    
    return render_template('admin/view_user.html',
                           user=user,
                           habits=habits,
                           habit_logs=habit_logs,
                           relapses=relapses,
                           total_habits=total_habits,
                           total_completions=total_completions,
                           total_relapses=total_relapses)


@admin_bp.route('/users/<user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    AuthService.toggle_user_active(user)
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.view_user', user_id=user_id))


@admin_bp.route('/users/<user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.view_user', user_id=user_id))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} has been deleted.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    from datetime import datetime, timezone, timedelta
    
    last_30_days = datetime.now(timezone.utc) - timedelta(days=30)
    
    daily_completions = db.session.query(
        db.func.date(HabitLog.completed_at).label('date'),
        db.func.count(HabitLog.id).label('count')
    ).filter(HabitLog.completed_at >= last_30_days)\
     .group_by(db.func.date(HabitLog.completed_at))\
     .order_by(db.func.date(HabitLog.completed_at)).all()
    
    daily_relapses = db.session.query(
        db.func.date(RelapseEvent.occurred_at).label('date'),
        db.func.count(RelapseEvent.id).label('count')
    ).filter(RelapseEvent.occurred_at >= last_30_days)\
     .group_by(db.func.date(RelapseEvent.occurred_at))\
     .order_by(db.func.date(RelapseEvent.occurred_at)).all()
    
    trigger_distribution = db.session.query(
        RelapseEvent.trigger_type,
        db.func.count(RelapseEvent.id).label('count')
    ).group_by(RelapseEvent.trigger_type).all()
    
    return render_template('admin/analytics.html',
                           daily_completions=daily_completions,
                           daily_relapses=daily_relapses,
                           trigger_distribution=trigger_distribution)
