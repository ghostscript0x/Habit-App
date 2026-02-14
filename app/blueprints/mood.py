from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services import MoodService
from app.models import MOOD_CHOICES
from datetime import date, timedelta

mood_bp = Blueprint('mood', __name__, url_prefix='/mood')


@mood_bp.route('/')
@login_required
def index():
    entries = MoodService.get_user_entries(current_user.id)
    trend = MoodService.get_mood_trend(current_user.id, days=30)
    distribution = MoodService.get_mood_distribution(current_user.id, days=30)
    avg_mood = MoodService.get_average_mood(current_user.id, days=30)
    return render_template('mood/index.html', 
                           entries=entries, 
                           mood_choices=MOOD_CHOICES,
                           trend=trend,
                           distribution=distribution,
                           avg_mood=avg_mood)


@mood_bp.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    today_entry = MoodService.get_today_entry(current_user.id)
    
    if request.method == 'POST':
        mood = request.form.get('mood')
        notes = request.form.get('notes')
        triggers = request.form.get('triggers')
        
        if not mood:
            flash('Mood selection is required', 'danger')
            return redirect(url_for('mood.log'))
        
        if today_entry:
            MoodService.update_entry(
                entry_id=today_entry.id,
                user_id=current_user.id,
                mood=mood,
                notes=notes,
                triggers=triggers
            )
            flash('Today\'s mood updated successfully', 'success')
        else:
            MoodService.create_entry(
                user_id=current_user.id,
                mood=mood,
                notes=notes,
                triggers=triggers
            )
            flash('Mood logged successfully', 'success')
        
        return redirect(url_for('mood.index'))
    
    return render_template('mood/log.html', mood_choices=MOOD_CHOICES, today_entry=today_entry)


@mood_bp.route('/<entry_id>/delete', methods=['POST'])
@login_required
def delete(entry_id):
    if MoodService.delete_entry(entry_id, current_user.id):
        flash('Mood entry deleted successfully', 'success')
    else:
        flash('Failed to delete mood entry', 'danger')
    return redirect(url_for('mood.index'))


@mood_bp.route('/trend')
@login_required
def trend():
    days = request.args.get('days', 30, type=int)
    trend = MoodService.get_mood_trend(current_user.id, days=days)
    return jsonify(trend)
