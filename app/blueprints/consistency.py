from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services import ConsistencyService

consistency_bp = Blueprint('consistency', __name__, url_prefix='/consistency')


@consistency_bp.route('/')
@login_required
def index():
    builders = ConsistencyService.get_user_builders(current_user.id)
    stats = ConsistencyService.get_builder_stats(current_user.id)
    return render_template('consistency/index.html', builders=builders, stats=stats)


@consistency_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        target_frequency = int(request.form.get('target_frequency', 1))
        
        if not name:
            flash('Builder name is required', 'danger')
            return redirect(url_for('consistency.create'))
        
        ConsistencyService.create_builder(
            user_id=current_user.id,
            name=name,
            description=description,
            target_frequency=target_frequency
        )
        flash('Consistency builder created successfully', 'success')
        return redirect(url_for('consistency.index'))
    
    return render_template('consistency/create.html')


@consistency_bp.route('/<builder_id>/complete', methods=['POST'])
@login_required
def complete(builder_id):
    builder = ConsistencyService.increment_completion(current_user.id, builder_id)
    if builder:
        flash(f'Streak increased to {builder.streak_count}!', 'success')
    else:
        flash('Builder not found', 'danger')
    return redirect(url_for('consistency.index'))


@consistency_bp.route('/<builder_id>/reset', methods=['POST'])
@login_required
def reset(builder_id):
    builder = ConsistencyService.reset_streak(current_user.id, builder_id)
    flash('Streak reset', 'warning')
    return redirect(url_for('consistency.index'))


@consistency_bp.route('/<builder_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(builder_id):
    builder = ConsistencyService.get_builder(current_user.id, builder_id)
    if not builder:
        flash('Builder not found', 'danger')
        return redirect(url_for('consistency.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        target_frequency = int(request.form.get('target_frequency', 1))
        is_active = request.form.get('is_active') == 'on'
        
        ConsistencyService.update_builder(
            builder_id=builder.id,
            user_id=current_user.id,
            name=name,
            description=description,
            target_frequency=target_frequency,
            is_active=is_active
        )
        flash('Builder updated successfully', 'success')
        return redirect(url_for('consistency.index'))
    
    return render_template('consistency/edit.html', builder=builder)


@consistency_bp.route('/<builder_id>/delete', methods=['POST'])
@login_required
def delete(builder_id):
    if ConsistencyService.delete_builder(builder_id, current_user.id):
        flash('Builder deleted successfully', 'success')
    else:
        flash('Failed to delete builder', 'danger')
    return redirect(url_for('consistency.index'))
