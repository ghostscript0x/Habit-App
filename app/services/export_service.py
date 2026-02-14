import csv
import io
from datetime import datetime
from app.models import Habit, HabitLog, RelapseEvent, JournalEntry, MoodEntry


class ExportService:
    
    @staticmethod
    def export_habits_csv(user_id):
        habits = Habit.query.filter_by(user_id=user_id).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Name', 'Description', 'Frequency', 'Active', 'Created At'])
        
        for habit in habits:
            writer.writerow([
                habit.id,
                habit.name,
                habit.description or '',
                habit.frequency,
                'Yes' if habit.is_active else 'No',
                habit.created_at.isoformat() if habit.created_at else ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_habit_logs_csv(user_id):
        logs = HabitLog.query.filter_by(user_id=user_id)\
            .order_by(HabitLog.completed_at.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Habit ID', 'Completed At', 'Streak Count', 'Notes'])
        
        for log in logs:
            writer.writerow([
                log.id,
                log.habit_id,
                log.completed_at.isoformat() if log.completed_at else '',
                log.streak_count,
                log.notes or ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_relapses_csv(user_id):
        relapses = RelapseEvent.query.filter_by(user_id=user_id)\
            .order_by(RelapseEvent.occurred_at.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Occurred At', 'Trigger Type', 'Severity', 'Notes'])
        
        for relapse in relapses:
            writer.writerow([
                relapse.id,
                relapse.occurred_at.isoformat() if relapse.occurred_at else '',
                relapse.trigger_type,
                relapse.severity,
                relapse.notes or ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_journal_csv(user_id):
        entries = JournalEntry.query.filter_by(user_id=user_id)\
            .order_by(JournalEntry.date.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Date', 'Content', 'Mood', 'Tags'])
        
        for entry in entries:
            writer.writerow([
                entry.id,
                entry.date.isoformat() if entry.date else '',
                entry.content.replace('\n', ' '),
                entry.mood or '',
                entry.tags or ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_mood_csv(user_id):
        entries = MoodEntry.query.filter_by(user_id=user_id)\
            .order_by(MoodEntry.date.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Date', 'Mood', 'Notes', 'Triggers'])
        
        for entry in entries:
            writer.writerow([
                entry.id,
                entry.date.isoformat() if entry.date else '',
                entry.mood,
                entry.notes or '',
                entry.triggers or ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_all_data(user_id):
        output = io.StringIO()
        output.write("=== HABITS ===\n")
        output.write(ExportService.export_habits_csv(user_id))
        output.write("\n=== HABIT LOGS ===\n")
        output.write(ExportService.export_habit_logs_csv(user_id))
        output.write("\n=== RELAPSES ===\n")
        output.write(ExportService.export_relapses_csv(user_id))
        output.write("\n=== JOURNAL ENTRIES ===\n")
        output.write(ExportService.export_journal_csv(user_id))
        output.write("\n=== MOOD ENTRIES ===\n")
        output.write(ExportService.export_mood_csv(user_id))
        return output.getvalue()
    
    @staticmethod
    def get_stats_summary(user_id):
        habits = Habit.query.filter_by(user_id=user_id).count()
        logs = HabitLog.query.filter_by(user_id=user_id).count()
        relapses = RelapseEvent.query.filter_by(user_id=user_id).count()
        journals = JournalEntry.query.filter_by(user_id=user_id).count()
        moods = MoodEntry.query.filter_by(user_id=user_id).count()
        
        return {
            'total_habits': habits,
            'total_completions': logs,
            'total_relapses': relapses,
            'total_journal_entries': journals,
            'total_mood_entries': moods
        }
