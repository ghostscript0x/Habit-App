from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services import JournalService
from app.models import MOOD_CHOICES
from datetime import date, datetime

journal_bp = Blueprint('journal', __name__, url_prefix='/journal')


@journal_bp.route('/')
@login_required
def index():
    entries = JournalService.get_user_entries(current_user.id)
    return render_template('journal/index.html', entries=entries, mood_choices=MOOD_CHOICES)


@journal_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        content = request.form.get('content')
        mood = request.form.get('mood')
        tags = request.form.get('tags')
        
        if not content:
            flash('Journal entry content is required', 'danger')
            return redirect(url_for('journal.create'))
        
        JournalService.create_entry(
            user_id=current_user.id,
            content=content,
            mood=mood,
            tags=tags
        )
        flash('Journal entry created successfully', 'success')
        return redirect(url_for('journal.index'))
    
    return render_template('journal/create.html', mood_choices=MOOD_CHOICES)


@journal_bp.route('/<entry_id>')
@login_required
def view(entry_id):
    entry = JournalService.get_entry(current_user.id, entry_id)
    if not entry:
        flash('Journal entry not found', 'danger')
        return redirect(url_for('journal.index'))
    return render_template('journal/view.html', entry=entry)


@journal_bp.route('/<entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(entry_id):
    entry = JournalService.get_entry(current_user.id, entry_id)
    if not entry:
        flash('Journal entry not found', 'danger')
        return redirect(url_for('journal.index'))
    
    if request.method == 'POST':
        content = request.form.get('content')
        mood = request.form.get('mood')
        tags = request.form.get('tags')
        
        JournalService.update_entry(
            entry_id=entry.id,
            user_id=current_user.id,
            content=content,
            mood=mood,
            tags=tags
        )
        flash('Journal entry updated successfully', 'success')
        return redirect(url_for('journal.view', entry_id=entry.id))
    
    return render_template('journal/edit.html', entry=entry, mood_choices=MOOD_CHOICES)


@journal_bp.route('/<entry_id>/delete', methods=['POST'])
@login_required
def delete(entry_id):
    if JournalService.delete_entry(entry_id, current_user.id):
        flash('Journal entry deleted successfully', 'success')
    else:
        flash('Failed to delete journal entry', 'danger')
    return redirect(url_for('journal.index'))
