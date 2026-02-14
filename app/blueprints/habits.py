from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services import HabitService, StreakService
from app.blueprints.forms import HabitForm, CompleteHabitForm

habits_bp = Blueprint('habits', __name__, url_prefix='/habits')


@habits_bp.route('/')
@login_required
def index():
    habits = HabitService.get_user_habits(current_user.id)
    habit_data = []
    for habit in habits:
        streak_info = StreakService.get_streak_info(habit)
        habit_data.append({
            'habit': habit,
            'current_streak': streak_info['current'],
            'longest_streak': streak_info['longest']
        })
    return render_template('habits/index.html', habit_data=habit_data)


@habits_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = HabitForm()
    if form.validate_on_submit():
        habit = HabitService.create_habit(
            user_id=current_user.id,
            name=form.name.data,
            description=form.description.data,
            frequency=form.frequency.data
        )
        flash(f'Habit "{habit.name}" created successfully!', 'success')
        return redirect(url_for('habits.index'))
    
    return render_template('habits/create.html', form=form)


@habits_bp.route('/<habit_id>')
@login_required
def view(habit_id):
    habit = HabitService.get_habit_by_id(habit_id)
    if not habit or habit.user_id != current_user.id:
        flash('Habit not found', 'danger')
        return redirect(url_for('habits.index'))
    
    streak_info = StreakService.get_streak_info(habit)
    logs = HabitService.get_habit_logs(habit_id, limit=20)
    
    return render_template('habits/view.html', habit=habit, streak_info=streak_info, logs=logs)


@habits_bp.route('/<habit_id>/complete', methods=['POST'])
@login_required
def complete(habit_id):
    form = CompleteHabitForm()
    habit = HabitService.get_habit_by_id(habit_id)
    
    if not habit or habit.user_id != current_user.id:
        return '', 404
    
    log = HabitService.complete_habit(habit_id, current_user.id, form.notes.data if form.notes.data else None)
    
    if request.headers.get('HX-Request'):
        streak_info = StreakService.get_streak_info(habit)
        return render_template('habits/partials/habit_card.html', 
                               habit=habit, 
                               current_streak=streak_info['current'],
                               longest_streak=streak_info['longest'])
    
    flash('Habit completed!', 'success')
    return redirect(url_for('habits.view', habit_id=habit_id))


@habits_bp.route('/<habit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(habit_id):
    habit = HabitService.get_habit_by_id(habit_id)
    if not habit or habit.user_id != current_user.id:
        flash('Habit not found', 'danger')
        return redirect(url_for('habits.index'))
    
    form = HabitForm(obj=habit)
    if form.validate_on_submit():
        HabitService.update_habit(habit_id,
                                   name=form.name.data,
                                   description=form.description.data,
                                   frequency=form.frequency.data)
        flash('Habit updated successfully!', 'success')
        return redirect(url_for('habits.view', habit_id=habit_id))
    
    return render_template('habits/edit.html', form=form, habit=habit)


@habits_bp.route('/<habit_id>/delete', methods=['POST'])
@login_required
def delete(habit_id):
    habit = HabitService.get_habit_by_id(habit_id)
    if not habit or habit.user_id != current_user.id:
        flash('Habit not found', 'danger')
        return redirect(url_for('habits.index'))
    
    HabitService.delete_habit(habit_id)
    flash('Habit deleted successfully!', 'success')
    return redirect(url_for('habits.index'))
