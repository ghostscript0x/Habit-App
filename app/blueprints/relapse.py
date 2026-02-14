from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timezone
from app.services import RelapseService
from app.blueprints.forms import RelapseEventForm

relapse_bp = Blueprint('relapse', __name__, url_prefix='/relapse')


@relapse_bp.route('/')
@login_required
def index():
    relapses = RelapseService.get_user_relapses(current_user.id, limit=50)
    stats = RelapseService.get_relapse_stats(current_user.id)
    return render_template('relapse/index.html', relapses=relapses, stats=stats)


@relapse_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = RelapseEventForm()
    if form.validate_on_submit():
        try:
            occurred_at = None
            if form.occurred_at.data:
                occurred_at = datetime.fromisoformat(form.occurred_at.data.replace('Z', '+00:00'))
            else:
                occurred_at = datetime.now(timezone.utc)
            
            relapse = RelapseService.create_relapse(
                user_id=current_user.id,
                occurred_at=occurred_at,
                trigger_type=form.trigger_type.data,
                severity=form.severity.data,
                notes=form.notes.data if form.notes.data else None
            )
            flash('Relapse event recorded. Remember, recovery is a journey.', 'success')
            return redirect(url_for('relapse.index'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('An error occurred while recording the event.', 'danger')
    
    return render_template('relapse/create.html', form=form)


@relapse_bp.route('/<relapse_id>')
@login_required
def view(relapse_id):
    relapse = RelapseService.get_relapse_by_id(relapse_id)
    if not relapse or relapse.user_id != current_user.id:
        flash('Relapse event not found', 'danger')
        return redirect(url_for('relapse.index'))
    
    return render_template('relapse/view.html', relapse=relapse)


@relapse_bp.route('/<relapse_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(relapse_id):
    relapse = RelapseService.get_relapse_by_id(relapse_id)
    if not relapse or relapse.user_id != current_user.id:
        flash('Relapse event not found', 'danger')
        return redirect(url_for('relapse.index'))
    
    form = RelapseEventForm(obj=relapse)
    if form.validate_on_submit():
        try:
            RelapseService.update_relapse(
                relapse_id,
                trigger_type=form.trigger_type.data,
                severity=form.severity.data,
                notes=form.notes.data
            )
            flash('Relapse event updated successfully!', 'success')
            return redirect(url_for('relapse.view', relapse_id=relapse_id))
        except ValueError as e:
            flash(str(e), 'danger')
    
    return render_template('relapse/edit.html', form=form, relapse=relapse)


@relapse_bp.route('/<relapse_id>/delete', methods=['POST'])
@login_required
def delete(relapse_id):
    relapse = RelapseService.get_relapse_by_id(relapse_id)
    if not relapse or relapse.user_id != current_user.id:
        flash('Relapse event not found', 'danger')
        return redirect(url_for('relapse.index'))
    
    RelapseService.delete_relapse(relapse_id)
    flash('Relapse event deleted successfully!', 'success')
    return redirect(url_for('relapse.index'))


@relapse_bp.route('/stats')
@login_required
def stats():
    stats = RelapseService.get_relapse_stats(current_user.id)
    recent = RelapseService.get_recent_relapses_days(current_user.id, days=30)
    return render_template('relapse/stats.html', stats=stats, recent=recent)
