from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services import AddictionKillerService

addiction_bp = Blueprint('addiction', __name__, url_prefix='/addiction')


@addiction_bp.route('/')
@login_required
def index():
    killers = AddictionKillerService.get_user_killers(current_user.id)
    most_used = AddictionKillerService.get_most_used_killers(current_user.id)
    most_effective = AddictionKillerService.get_most_effective_killers(current_user.id)
    return render_template('addiction/index.html', 
                           killers=killers, 
                           most_used=most_used,
                           most_effective=most_effective,
                           technique_info=AddictionKillerService.TECHNIQUE_INFO)


@addiction_bp.route('/techniques')
@login_required
def techniques():
    return jsonify(AddictionKillerService.TECHNIQUE_INFO)


@addiction_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        technique = request.form.get('technique')
        target_addiction = request.form.get('target_addiction')
        notes = request.form.get('notes')
        
        if not name or not technique:
            flash('Name and technique are required', 'danger')
            return redirect(url_for('addiction.create'))
        
        AddictionKillerService.create_killer(
            user_id=current_user.id,
            name=name,
            technique=technique,
            target_addiction=target_addiction,
            notes=notes
        )
        flash('Addiction killer created successfully', 'success')
        return redirect(url_for('addiction.index'))
    
    techniques = AddictionKillerService.TECHNIQUE_INFO
    return render_template('addiction/create.html', techniques=techniques)


@addiction_bp.route('/use/<killer_id>', methods=['GET', 'POST'])
@login_required
def use(killer_id):
    killer = AddictionKillerService.get_killer(current_user.id, killer_id)
    if not killer:
        flash('Addiction killer not found', 'danger')
        return redirect(url_for('addiction.index'))
    
    technique_info = AddictionKillerService.get_technique_info(killer.technique)
    
    if request.method == 'POST':
        craving_intensity = int(request.form.get('craving_intensity', 5))
        notes = request.form.get('notes')
        
        session = AddictionKillerService.use_killer(
            user_id=current_user.id,
            killer_id=killer_id,
            craving_intensity=craving_intensity,
            notes=notes
        )
        flash(f'Great job using {killer.name}! Keep fighting!', 'success')
        return redirect(url_for('addiction.history', killer_id=killer_id))
    
    return render_template('addiction/use.html', killer=killer, technique_info=technique_info)


@addiction_bp.route('/history/<killer_id>')
@login_required
def history(killer_id):
    killer = AddictionKillerService.get_killer(current_user.id, killer_id)
    if not killer:
        flash('Addiction killer not found', 'danger')
        return redirect(url_for('addiction.index'))
    
    sessions = AddictionKillerService.get_killer_sessions(current_user.id, killer_id)
    return render_template('addiction/history.html', killer=killer, sessions=sessions)


@addiction_bp.route('/<killer_id>/rate', methods=['POST'])
@login_required
def rate(killer_id):
    rating = int(request.form.get('rating', 5))
    AddictionKillerService.rate_effectiveness(killer_id, current_user.id, rating)
    flash('Effectiveness rating saved', 'success')
    return redirect(url_for('addiction.index'))


@addiction_bp.route('/<killer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(killer_id):
    killer = AddictionKillerService.get_killer(current_user.id, killer_id)
    if not killer:
        flash('Addiction killer not found', 'danger')
        return redirect(url_for('addiction.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        target_addiction = request.form.get('target_addiction')
        notes = request.form.get('notes')
        is_active = request.form.get('is_active') == 'on'
        
        AddictionKillerService.update_killer(
            killer_id=killer.id,
            user_id=current_user.id,
            name=name,
            target_addiction=target_addiction,
            notes=notes,
            is_active=is_active
        )
        flash('Addiction killer updated successfully', 'success')
        return redirect(url_for('addiction.index'))
    
    techniques = AddictionKillerService.TECHNIQUE_INFO
    return render_template('addiction/edit.html', killer=killer, techniques=techniques)


@addiction_bp.route('/<killer_id>/delete', methods=['POST'])
@login_required
def delete(killer_id):
    if AddictionKillerService.delete_killer(killer_id, current_user.id):
        flash('Addiction killer deleted successfully', 'success')
    else:
        flash('Failed to delete addiction killer', 'danger')
    return redirect(url_for('addiction.index'))
