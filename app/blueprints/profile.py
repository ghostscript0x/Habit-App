from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models import User, Habit, HABIT_TEMPLATES, HabitLog, MOOD_CHOICES, JournalEntry, MoodEntry
from app.models.social import PreventionPlan, CommunityPost, CommunityComment, UserReport
from app.services import AuthService
from datetime import datetime, timezone, timedelta, date
from wtforms import StringField, PasswordField, TextAreaField, SelectField, TimeField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from flask_wtf import FlaskForm

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    theme = SelectField('Theme', choices=[('light', 'Light'), ('dark', 'Dark')])
    submit = SubmitField('Update Profile')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')


class PreventionPlanForm(FlaskForm):
    title = StringField('Plan Title', validators=[DataRequired()])
    warning_signs = TextAreaField('Warning Signs', validators=[Optional()])
    coping_strategies = TextAreaField('Coping Strategies', validators=[Optional()])
    support_people = TextAreaField('Support People', validators=[Optional()])
    activities = TextAreaField('Healthy Activities', validators=[Optional()])
    submit = SubmitField('Save Plan')


class ReportForm(FlaskForm):
    reason = SelectField('Reason', choices=[
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit Report')


@profile_bp.route('/')
@login_required
def index():
    total_habits = Habit.query.filter_by(user_id=current_user.id, is_active=True).count()
    total_completions = HabitLog.query.filter_by(user_id=current_user.id).count()
    total_journals = JournalEntry.query.filter_by(user_id=current_user.id).count()
    total_moods = MoodEntry.query.filter_by(user_id=current_user.id).count()
    
    last_7_days = datetime.now(timezone.utc) - timedelta(days=7)
    weekly_completions = HabitLog.query.filter(
        HabitLog.user_id == current_user.id,
        HabitLog.completed_at >= last_7_days
    ).count()
    
    return render_template('profile/index.html',
                          total_habits=total_habits,
                          total_completions=total_completions,
                          total_journals=total_journals,
                          total_moods=total_moods,
                          weekly_completions=weekly_completions)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = ProfileForm()
    
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.theme.data = current_user.theme or 'light'
    
    if form.validate_on_submit():
        if User.query.filter(User.username == form.username.data, User.id != current_user.id).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('profile.edit'))
        
        if User.query.filter(User.email == form.email.data, User.id != current_user.id).first():
            flash('Email already in use.', 'danger')
            return redirect(url_for('profile.edit'))
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.theme = form.theme.data
        db.session.commit()
        
        flash('Profile updated!', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('profile/edit.html', form=form)


@profile_bp.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not bcrypt.check_password_hash(current_user.password_hash, form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('profile.password'))
        
        current_user.password_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('profile/password.html', form=form)


@profile_bp.route('/prevention-plans')
@login_required
def prevention_plans():
    plans = PreventionPlan.query.filter_by(user_id=current_user.id).order_by(PreventionPlan.created_at.desc()).all()
    return render_template('profile/prevention_plans.html', plans=plans)


@profile_bp.route('/prevention-plans/create', methods=['GET', 'POST'])
@login_required
def create_prevention_plan():
    form = PreventionPlanForm()
    
    if form.validate_on_submit():
        plan = PreventionPlan()
        plan.user_id = current_user.id
        plan.title = form.title.data
        plan.warning_signs = form.warning_signs.data
        plan.coping_strategies = form.coping_strategies.data
        plan.support_people = form.support_people.data
        plan.activities = form.activities.data
        db.session.add(plan)
        db.session.commit()
        
        flash('Prevention plan created!', 'success')
        return redirect(url_for('profile.prevention_plans'))
    
    return render_template('profile/create_prevention_plan.html', form=form)


@profile_bp.route('/prevention-plans/<plan_id>/toggle', methods=['POST'])
@login_required
def toggle_prevention_plan(plan_id):
    plan = PreventionPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    plan.is_active = not plan.is_active
    db.session.commit()
    
    status = 'activated' if plan.is_active else 'deactivated'
    flash(f'Plan {status}!', 'success')
    return redirect(url_for('profile.prevention_plans'))


@profile_bp.route('/prevention-plans/<plan_id>/delete', methods=['POST'])
@login_required
def delete_prevention_plan(plan_id):
    plan = PreventionPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    db.session.delete(plan)
    db.session.commit()
    
    flash('Plan deleted!', 'success')
    return redirect(url_for('profile.prevention_plans'))


@profile_bp.route('/use-streak-freeze', methods=['POST'])
@login_required
def use_streak_freeze():
    if current_user.streak_freezes > 0:
        current_user.streak_freezes -= 1
        db.session.commit()
        flash('Streak freeze used! Your streak is protected for today.', 'success')
    else:
        flash('You don\'t have any streak freezes.', 'danger')
    return redirect(url_for('profile.index'))


@profile_bp.route('/export-data')
@login_required
def export_data():
    from app.services.export_service import ExportService
    data = ExportService.export_all_user_data(current_user.id)
    return jsonify(data)


@profile_bp.route('/theme', methods=['POST'])
@login_required
def set_theme():
    theme = request.form.get('theme')
    if theme in ['light', 'dark']:
        current_user.theme = theme
        db.session.commit()
    return jsonify({'success': True, 'theme': theme})
