import csv
import io
import json
from datetime import datetime
from app.models import Habit, HabitLog, RelapseEvent, JournalEntry, MoodEntry, Trigger, UserAchievement
from app.models.social import PreventionPlan, CommunityPost
from app.models import Partnership, SharedGoal


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
    
    @staticmethod
    def export_all_user_data(user_id):
        data = {
            'exported_at': datetime.now().isoformat(),
            'user_id': user_id,
            'habits': [],
            'habit_logs': [],
            'relapses': [],
            'journal_entries': [],
            'mood_entries': [],
            'triggers': [],
            'achievements': [],
            'prevention_plans': [],
            'partnerships': [],
            'shared_goals': []
        }
        
        for habit in Habit.query.filter_by(user_id=user_id).all():
            data['habits'].append({
                'id': habit.id,
                'name': habit.name,
                'description': habit.description,
                'frequency': habit.frequency,
                'category': habit.category,
                'is_active': habit.is_active,
                'created_at': habit.created_at.isoformat() if habit.created_at else None
            })
        
        for log in HabitLog.query.filter_by(user_id=user_id).all():
            data['habit_logs'].append({
                'id': log.id,
                'habit_id': log.habit_id,
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'streak_count': log.streak_count,
                'notes': log.notes
            })
        
        for relapse in RelapseEvent.query.filter_by(user_id=user_id).all():
            data['relapses'].append({
                'id': relapse.id,
                'occurred_at': relapse.occurred_at.isoformat() if relapse.occurred_at else None,
                'trigger_type': relapse.trigger_type,
                'severity': relapse.severity,
                'notes': relapse.notes
            })
        
        for entry in JournalEntry.query.filter_by(user_id=user_id).all():
            data['journal_entries'].append({
                'id': entry.id,
                'date': entry.date.isoformat() if entry.date else None,
                'content': entry.content,
                'mood': entry.mood,
                'tags': entry.tags
            })
        
        for entry in MoodEntry.query.filter_by(user_id=user_id).all():
            data['mood_entries'].append({
                'id': entry.id,
                'date': entry.date.isoformat() if entry.date else None,
                'mood': entry.mood,
                'notes': entry.notes,
                'triggers': entry.triggers
            })
        
        for trigger in Trigger.query.filter_by(user_id=user_id).all():
            data['triggers'].append({
                'id': trigger.id,
                'name': trigger.name,
                'category': trigger.category,
                'description': trigger.description,
                'is_active': trigger.is_active
            })
        
        for ua in UserAchievement.query.filter_by(user_id=user_id).all():
            data['achievements'].append({
                'achievement_id': ua.achievement_id,
                'earned_at': ua.earned_at.isoformat() if ua.earned_at else None
            })
        
        for plan in PreventionPlan.query.filter_by(user_id=user_id).all():
            data['prevention_plans'].append({
                'id': plan.id,
                'title': plan.title,
                'warning_signs': plan.warning_signs,
                'coping_strategies': plan.coping_strategies,
                'support_people': plan.support_people,
                'activities': plan.activities,
                'is_active': plan.is_active
            })
        
        for p in Partnership.query.filter(
            (Partnership.user1_id == user_id) | (Partnership.user2_id == user_id)
        ).all():
            partner_id = p.user2_id if p.user1_id == user_id else p.user1_id
            data['partnerships'].append({
                'id': p.id,
                'partner_id': partner_id,
                'status': p.status,
                'created_at': p.created_at.isoformat() if p.created_at else None
            })
            
            for goal in SharedGoal.query.filter_by(partnership_id=p.id).all():
                data['shared_goals'].append({
                    'id': goal.id,
                    'partnership_id': goal.partnership_id,
                    'title': goal.title,
                    'description': goal.description,
                    'frequency': goal.frequency,
                    'category': goal.category,
                    'is_completed': goal.is_completed,
                    'created_at': goal.created_at.isoformat() if goal.created_at else None
                })
        
        return data
