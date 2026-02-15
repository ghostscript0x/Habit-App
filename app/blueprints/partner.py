from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.partnership import Partnership, SharedGoal, SharedGoalProgress, GoalMilestone, PartnerMessage
from app.models import Notification, User
from datetime import datetime, timezone, timedelta
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

partner_bp = Blueprint('partner', __name__, url_prefix='/partner')

GOAL_CATEGORIES = [
    ('', 'No Category'),
    ('health', 'Health'),
    ('mental', 'Mental Health'),
    ('habits', 'Habits'),
    ('fitness', 'Fitness'),
    ('learning', 'Learning'),
    ('career', 'Career'),
    ('relationships', 'Relationships'),
]


class PartnershipForm(FlaskForm):
    search = StringField('Search by username or email')
    submit = SubmitField('Search')


class SharedGoalForm(FlaskForm):
    title = StringField('Goal Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    frequency = SelectField('Frequency', choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('minutely', 'Minutely')], default='daily')
    category = SelectField('Category', choices=GOAL_CATEGORIES, default='')
    target_date = DateField('Target Date', format='%Y-%m-%d')
    submit = SubmitField('Create Goal')


class MilestoneForm(FlaskForm):
    title = StringField('Milestone Title', validators=[DataRequired()])
    submit = SubmitField('Add Milestone')


class MessageForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')


def create_notification(user_id, title, message, notification_type='general', link=None):
    notification = Notification()
    notification.user_id = user_id
    notification.title = title
    notification.message = message
    notification.notification_type = notification_type
    notification.link = link
    db.session.add(notification)
    return notification


@partner_bp.route('/')
@login_required
def index():
    partnerships = Partnership.query.filter(
        ((Partnership.user1_id == current_user.id) | (Partnership.user2_id == current_user.id)) &
        (Partnership.status == 'accepted')
    ).all()
    
    pending = Partnership.query.filter(
        (Partnership.user2_id == current_user.id) &
        (Partnership.status == 'pending')
    ).all()
    
    sent_requests = Partnership.query.filter(
        (Partnership.user1_id == current_user.id) &
        (Partnership.status == 'pending')
    ).all()
    
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()
    
    return render_template('partner/index.html',
                          partnerships=partnerships,
                          pending=pending,
                          sent_requests=sent_requests,
                          unread_notifications=unread_notifications)


@partner_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search_partner():
    form = PartnershipForm()
    results = []
    
    if form.validate_on_submit():
        search_term = form.search.data
        results = User.query.filter(
            (User.username.ilike(f'%{search_term}%')) |
            (User.email.ilike(f'%{search_term}%'))
        ).filter(User.id != current_user.id).limit(10).all()
    
    return render_template('partner/search.html', form=form, results=results)


@partner_bp.route('/request', methods=['GET', 'POST'])
@login_required
def request_partnership():
    form = PartnershipForm()
    
    if form.validate_on_submit():
        search_term = form.search.data
        partner = User.query.filter(
            (User.email == search_term) | (User.username == search_term)
        ).first()
        
        if not partner:
            flash('No user found with that email or username.', 'danger')
            return redirect(url_for('partner.request_partnership'))
        
        if partner.id == current_user.id:
            flash('You cannot partner with yourself.', 'danger')
            return redirect(url_for('partner.request_partnership'))
        
        existing = Partnership.query.filter(
            ((Partnership.user1_id == current_user.id) & (Partnership.user2_id == partner.id)) |
            ((Partnership.user1_id == partner.id) & (Partnership.user2_id == current_user.id))
        ).first()
        
        if existing:
            if existing.status == 'accepted':
                flash('Partnership already exists.', 'warning')
            else:
                flash('Partnership request already exists.', 'warning')
            return redirect(url_for('partner.index'))
        
        partnership = Partnership()
        partnership.user1_id = current_user.id
        partnership.user2_id = partner.id
        partnership.status = 'pending'
        db.session.add(partnership)
        
        create_notification(
            partner.id,
            'New Partner Request',
            f'{current_user.username} sent you a partnership request.',
            'partnership',
            url_for('partner.index')
        )
        
        db.session.commit()
        
        flash(f'Partnership request sent to {partner.username}!', 'success')
        return redirect(url_for('partner.index'))
    
    return render_template('partner/request.html', form=form)


@partner_bp.route('/accept/<partnership_id>')
@login_required
def accept_partnership(partnership_id):
    partnership = Partnership.query.get_or_404(partnership_id)
    
    if partnership.user2_id != current_user.id:
        flash('Invalid request.', 'danger')
        return redirect(url_for('partner.index'))
    
    partnership.status = 'accepted'
    db.session.commit()
    
    create_notification(
        partnership.user1_id,
        'Partner Request Accepted',
        f'{current_user.username} accepted your partnership request!',
        'partnership',
        url_for('partner.index')
    )
    db.session.commit()
    
    flash('Partnership accepted! You can now set goals together.', 'success')
    return redirect(url_for('partner.index'))


@partner_bp.route('/decline/<partnership_id>')
@login_required
def decline_partnership(partnership_id):
    partnership = Partnership.query.get_or_404(partnership_id)
    
    if partnership.user2_id != current_user.id:
        flash('Invalid request.', 'danger')
        return redirect(url_for('partner.index'))
    
    create_notification(
        partnership.user1_id,
        'Partner Request Declined',
        f'{current_user.username} declined your partnership request.',
        'partnership',
        url_for('partner.index')
    )
    
    db.session.delete(partnership)
    db.session.commit()
    
    flash('Partnership request declined.', 'info')
    return redirect(url_for('partner.index'))


@partner_bp.route('/cancel/<partnership_id>')
@login_required
def cancel_partnership(partnership_id):
    partnership = Partnership.query.get_or_404(partnership_id)
    
    if current_user.id not in [partnership.user1_id, partnership.user2_id]:
        flash('Invalid access.', 'danger')
        return redirect(url_for('partner.index'))
    
    partner = partnership.get_partner(current_user.id)
    
    create_notification(
        partner.id,
        'Partnership Ended',
        f'{current_user.username} ended your partnership.',
        'partnership',
        url_for('partner.index')
    )
    
    db.session.delete(partnership)
    db.session.commit()
    
    flash('Partnership has been ended.', 'info')
    return redirect(url_for('partner.index'))


@partner_bp.route('/<partnership_id>/goals')
@login_required
def goals(partnership_id):
    partnership = Partnership.query.get_or_404(partnership_id)
    
    if current_user.id not in [partnership.user1_id, partnership.user2_id]:
        flash('Invalid access.', 'danger')
        return redirect(url_for('partner.index'))
    
    goals = SharedGoal.query.filter_by(partnership_id=partnership_id)\
        .order_by(SharedGoal.created_at.desc()).all()
    
    partner = partnership.get_partner(current_user.id)
    
    return render_template('partner/goals.html',
                          partnership=partnership,
                          partner=partner,
                          goals=goals,
                          categories=GOAL_CATEGORIES)


@partner_bp.route('/<partnership_id>/goals/create', methods=['GET', 'POST'])
@login_required
def create_goal(partnership_id):
    partnership = Partnership.query.get_or_404(partnership_id)
    
    if current_user.id not in [partnership.user1_id, partnership.user2_id]:
        flash('Invalid access.', 'danger')
        return redirect(url_for('partner.index'))
    
    form = SharedGoalForm()
    form.category.choices = GOAL_CATEGORIES
    
    if form.validate_on_submit():
        goal = SharedGoal()
        goal.partnership_id = partnership_id
        goal.title = form.title.data
        goal.description = form.description.data
        goal.frequency = form.frequency.data
        goal.category = form.category.data if form.category.data else None
        goal.target_date = form.target_date.data
        db.session.add(goal)
        
        partner = partnership.get_partner(current_user.id)
        create_notification(
            partner.id,
            'New Shared Goal',
            f'{current_user.username} created a new goal: {goal.title}',
            'goal',
            url_for('partner.goals', partnership_id=partnership_id)
        )
        
        db.session.commit()
        
        flash('Shared goal created!', 'success')
        return redirect(url_for('partner.goals', partnership_id=partnership_id))
    
    return render_template('partner/create_goal.html', form=form, partnership=partnership)


@partner_bp.route('/goals/<goal_id>/complete', methods=['POST'])
@login_required
def complete_goal(goal_id):
    goal = SharedGoal.query.get_or_404(goal_id)
    partnership = goal.partnership
    
    if current_user.id not in [partnership.user1_id, partnership.user2_id]:
        flash('Invalid access.', 'danger')
        return redirect(url_for('partner.index'))
    
    progress_user_ids = set(p.user_id for p in goal.progress_entries)
    if partnership.user1_id not in progress_user_ids or partnership.user2_id not in progress_user_ids:
        flash('Both partners must add progress before completing the goal.', 'warning')
        return redirect(url_for('partner.goals', partnership_id=partnership.id))
    
    goal.is_completed = True
    goal.completed_at = datetime.now(timezone.utc)
    
    partner = partnership.get_partner(current_user.id)
    create_notification(
        partner.id,
        'Goal Completed!',
        f'{current_user.username} completed the goal: {goal.title}',
        'goal',
        url_for('partner.goals', partnership_id=partnership.id)
    )
    
    db.session.commit()
    
    flash('Goal marked as completed!', 'success')
    return redirect(url_for('partner.goals', partnership_id=partnership.id))


@partner_bp.route('/goals/<goal_id>/progress', methods=['POST'])
@login_required
def add_progress(goal_id):
    goal = SharedGoal.query.get_or_404(goal_id)
    partnership = goal.partnership
    
    if current_user.id not in [partnership.user1_id, partnership.user2_id]:
        flash('Invalid access.', 'danger')
        return redirect(url_for('partner.index'))
    
    progress_notes = request.form.get('progress', '')
    
    progress = SharedGoalProgress()
    progress.shared_goal_id = goal_id
    progress.user_id = current_user.id
    progress.notes = progress_notes
    db.session.add(progress)
    
    partner = partnership.get_partner(current_user.id)
    create_notification(
        partner.id,
        'Partner Progress Update',
        f'{current_user.username} added progress to "{goal.title}": {progress_notes}',
        'goal',
        url_for('partner.goals', partnership_id=partnership.id)
    )
    
    db.session.commit()
    
    flash('Progress updated!', 'success')
    return redirect(url_for('partner.goals', partnership_id=partnership.id))


@partner_bp.route('/goals/<goal_id>/milestones/add', methods=['POST'])
@login_required
def add_milestone(goal_id):
    goal = SharedGoal.query.get_or_404(goal_id)
    partnership = goal.partnership
    
    if current_user.id not in [partnership.user1_id, partnership.user2_id]:
        flash('Invalid access.', 'danger')
        return redirect(url_for('partner.index'))
    
    title = request.form.get('title')
    if not title:
        flash('Milestone title is required.', 'danger')
        return redirect(url_for('partner.goals', partnership_id=partnership.id))
    
    last_milestone = GoalMilestone.query.filter_by(goal_id=goal_id).order_by(GoalMilestone.order.desc()).first()
    order = (last_milestone.order + 1) if last_milestone else 0
    
    milestone = GoalMilestone()
    milestone.goal_id = goal_id
    milestone.title = title
    milestone.order = order
    db.session.add(milestone)
    
    partner = partnership.get_partner(current_user.id)
    create_notification(
        partner.id,
        'New Milestone Added',
        f'{current_user.username} added a milestone to "{goal.title}"',
        'goal',
        url_for('partner.goals', partnership_id=partnership.id)
    )
    
    db.session.commit()
    
    flash('Milestone added!', 'success')
    return redirect(url_for('partner.goals', partnership_id=partnership.id))


@partner_bp.route('/milestones/<milestone_id>/complete', methods=['POST'])
@login_required
def complete_milestone(milestone_id):
    milestone = GoalMilestone.query.get_or_404(milestone_id)
    goal = milestone.goal
    partnership = goal.partnership
    
    if current_user.id not in [partnership.user1_id, partnership.user2_id]:
        flash('Invalid access.', 'danger')
        return redirect(url_for('partner.index'))
    
    milestone.is_completed = True
    milestone.completed_at = datetime.now(timezone.utc)
    
    partner = partnership.get_partner(current_user.id)
    create_notification(
        partner.id,
        'Milestone Completed',
        f'{current_user.username} completed milestone "{milestone.title}" in "{goal.title}"',
        'goal',
        url_for('partner.goals', partnership_id=partnership.id)
    )
    
    db.session.commit()
    
    flash('Milestone completed!', 'success')
    return redirect(url_for('partner.goals', partnership_id=partnership.id))


@partner_bp.route('/<partnership_id>/chat')
@login_required
def chat(partnership_id):
    partnership = Partnership.query.get_or_404(partnership_id)
    
    if current_user.id not in [partnership.user1_id, partnership.user2_id]:
        flash('Invalid access.', 'danger')
        return redirect(url_for('partner.index'))
    
    partner = partnership.get_partner(current_user.id)
    messages = PartnerMessage.query.filter_by(partnership_id=partnership_id)\
        .order_by(PartnerMessage.created_at.asc()).all()
    
    PartnerMessage.query.filter(
        PartnerMessage.partnership_id == partnership_id,
        PartnerMessage.sender_id != current_user.id,
        PartnerMessage.is_read == False
    ).update({'is_read': True})
    db.session.commit()
    
    return render_template('partner/chat.html',
                          partnership=partnership,
                          partner=partner,
                          messages=messages)


@partner_bp.route('/<partnership_id>/chat/send', methods=['POST'])
@login_required
def send_message(partnership_id):
    partnership = Partnership.query.get_or_404(partnership_id)
    
    if current_user.id not in [partnership.user1_id, partnership.user2_id]:
        flash('Invalid access.', 'danger')
        return redirect(url_for('partner.index'))
    
    message_text = request.form.get('message')
    if not message_text:
        flash('Message cannot be empty.', 'danger')
        return redirect(url_for('partner.chat', partnership_id=partnership_id))
    
    message = PartnerMessage()
    message.partnership_id = partnership_id
    message.sender_id = current_user.id
    message.message = message_text
    db.session.add(message)
    
    partner = partnership.get_partner(current_user.id)
    create_notification(
        partner.id,
        'New Message',
        f'{current_user.username} sent you a message.',
        'message',
        url_for('partner.chat', partnership_id=partnership_id)
    )
    
    db.session.commit()
    
    flash('Message sent!', 'success')
    return redirect(url_for('partner.chat', partnership_id=partnership_id))


@partner_bp.route('/<partnership_id>/stats')
@login_required
def partner_stats(partnership_id):
    partnership = Partnership.query.get_or_404(partnership_id)
    
    if current_user.id not in [partnership.user1_id, partnership.user2_id]:
        flash('Invalid access.', 'danger')
        return redirect(url_for('partner.index'))
    
    partner = partnership.get_partner(current_user.id)
    
    from app.models import HabitLog, Habit
    
    partner_habits = Habit.query.filter_by(user_id=partner.id, is_active=True).all()
    partner_habit_ids = [h.id for h in partner_habits]
    
    partner_completions = HabitLog.query.filter(
        HabitLog.habit_id.in_(partner_habit_ids)
    ).count() if partner_habit_ids else 0
    
    last_7_days = datetime.now(timezone.utc) - timedelta(days=7)
    partner_weekly = HabitLog.query.filter(
        HabitLog.habit_id.in_(partner_habit_ids),
        HabitLog.completed_at >= last_7_days
    ).count() if partner_habit_ids else 0
    
    goals = SharedGoal.query.filter_by(partnership_id=partnership_id).all()
    completed_goals = sum(1 for g in goals if g.is_completed)
    
    return render_template('partner/stats.html',
                          partnership=partnership,
                          partner=partner,
                          partner_completions=partner_completions,
                          partner_weekly=partner_weekly,
                          completed_goals=completed_goals,
                          total_goals=len(goals))


@partner_bp.route('/<partnership_id>/calendar')
@login_required
def calendar(partnership_id):
    partnership = Partnership.query.get_or_404(partnership_id)
    
    if current_user.id not in [partnership.user1_id, partnership.user2_id]:
        flash('Invalid access.', 'danger')
        return redirect(url_for('partner.index'))
    
    goals = SharedGoal.query.filter_by(partnership_id=partnership_id).all()
    partner = partnership.get_partner(current_user.id)
    
    return render_template('partner/calendar.html',
                          partnership=partnership,
                          partner=partner,
                          goals=goals)


@partner_bp.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).limit(50).all()
    
    return render_template('partner/notifications.html', notifications=notifs)


@partner_bp.route('/notifications/mark-read/<notif_id>', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first()
    if notif:
        notif.is_read = True
        db.session.commit()
    
    if notif and notif.link:
        return redirect(notif.link)
    return redirect(url_for('partner.notifications'))


@partner_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False)\
        .update({'is_read': True})
    db.session.commit()
    
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('partner.notifications'))


@partner_bp.route('/notifications/count')
@login_required
def notification_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})
