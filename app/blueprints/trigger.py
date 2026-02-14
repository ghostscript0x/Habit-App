from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services import TriggerService

trigger_bp = Blueprint('trigger', __name__, url_prefix='/triggers')


@trigger_bp.route('/')
@login_required
def index():
    triggers = TriggerService.get_user_triggers(current_user.id)
    stats = TriggerService.get_trigger_stats(current_user.id)
    return render_template('trigger/index.html', triggers=triggers, stats=stats)


@trigger_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        
        if not name:
            flash('Trigger name is required', 'danger')
            return redirect(url_for('trigger.create'))
        
        TriggerService.create_trigger(
            user_id=current_user.id,
            name=name,
            description=description,
            category=category
        )
        flash('Trigger created successfully', 'success')
        return redirect(url_for('trigger.index'))
    
    return render_template('trigger/create.html')


@trigger_bp.route('/<trigger_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(trigger_id):
    trigger = TriggerService.get_trigger(current_user.id, trigger_id)
    if not trigger:
        flash('Trigger not found', 'danger')
        return redirect(url_for('trigger.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        is_active = request.form.get('is_active') == 'on'
        
        TriggerService.update_trigger(
            trigger_id=trigger.id,
            user_id=current_user.id,
            name=name,
            description=description,
            category=category,
            is_active=is_active
        )
        flash('Trigger updated successfully', 'success')
        return redirect(url_for('trigger.index'))
    
    return render_template('trigger/edit.html', trigger=trigger)


@trigger_bp.route('/<trigger_id>/delete', methods=['POST'])
@login_required
def delete(trigger_id):
    if TriggerService.delete_trigger(trigger_id, current_user.id):
        flash('Trigger deleted successfully', 'success')
    else:
        flash('Failed to delete trigger', 'danger')
    return redirect(url_for('trigger.index'))


@trigger_bp.route('/<trigger_id>/encountered', methods=['POST'])
@login_required
def encountered(trigger_id):
    TriggerService.increment_encountered(trigger_id, current_user.id)
    flash('Trigger encounter recorded', 'success')
    return redirect(url_for('trigger.index'))


@trigger_bp.route('/<trigger_id>/overcome', methods=['POST'])
@login_required
def overcome(trigger_id):
    TriggerService.increment_overcome(trigger_id, current_user.id)
    flash('Trigger overcome recorded - Great job!', 'success')
    return redirect(url_for('trigger.index'))
