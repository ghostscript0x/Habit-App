from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Partnership, SharedGoal, SharedGoalProgress, User
from datetime import datetime, timezone
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

partner_bp = Blueprint('partner', __name__, url_prefix='/partner')


class PartnershipForm(FlaskForm):
    partner_email = StringField('Partner Email', validators=[DataRequired()])
    submit = SubmitField('Send Request')


class SharedGoalForm(FlaskForm):
    title = StringField('Goal Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    target_date = DateField('Target Date', format='%Y-%m-%d')
    submit = SubmitField('Create Goal')


class GoalProgressForm(FlaskForm):
    progress = StringField('Progress Notes')
    submit = SubmitField('Update Progress')


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
    
    return render_template('partner/index.html',
                          partnerships=partnerships,
                          pending=pending,
                          sent_requests=sent_requests)


@partner_bp.route('/request', methods=['GET', 'POST'])
@login_required
def request_partnership():
    form = PartnershipForm()
    
    if form.validate_on_submit():
        partner = User.query.filter_by(email=form.partner_email.data).first()
        
        if not partner:
            flash('No user found with that email.', 'danger')
            return redirect(url_for('partner.request_partnership'))
        
        if partner.id == current_user.id:
            flash('You cannot partner with yourself.', 'danger')
            return redirect(url_for('partner.request_partnership'))
        
        existing = Partnership.query.filter(
            ((Partnership.user1_id == current_user.id) & (Partnership.user2_id == partner.id)) |
            ((Partnership.user1_id == partner.id) & (Partnership.user2_id == current_user.id))
        ).first()
        
        if existing:
            flash('Partnership request already exists.', 'warning')
            return redirect(url_for('partner.index'))
        
        partnership = Partnership()
        partnership.user1_id = current_user.id
        partnership.user2_id = partner.id
        partnership.status = 'pending'
        db.session.add(partnership)
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
    
    flash('Partnership accepted! You can now set goals together.', 'success')
    return redirect(url_for('partner.index'))


@partner_bp.route('/decline/<partnership_id>')
@login_required
def decline_partnership(partnership_id):
    partnership = Partnership.query.get_or_404(partnership_id)
    
    if partnership.user2_id != current_user.id:
        flash('Invalid request.', 'danger')
        return redirect(url_for('partner.index'))
    
    db.session.delete(partnership)
    db.session.commit()
    
    flash('Partnership request declined.', 'info')
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
                          goals=goals)


@partner_bp.route('/<partnership_id>/goals/create', methods=['GET', 'POST'])
@login_required
def create_goal(partnership_id):
    partnership = Partnership.query.get_or_404(partnership_id)
    
    if current_user.id not in [partnership.user1_id, partnership.user2_id]:
        flash('Invalid access.', 'danger')
        return redirect(url_for('partner.index'))
    
    form = SharedGoalForm()
    
    if form.validate_on_submit():
        goal = SharedGoal()
        goal.partnership_id = partnership_id
        goal.title = form.title.data
        goal.description = form.description.data
        goal.target_date = form.target_date.data
        db.session.add(goal)
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
    
    goal.is_completed = True
    goal.completed_at = datetime.now(timezone.utc)
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
    db.session.commit()
    
    flash('Progress updated!', 'success')
    return redirect(url_for('partner.goals', partnership_id=partnership.id))
