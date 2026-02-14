from datetime import datetime, timezone
from app import db
from app.models import AddictionKiller, AddictionSession


class AddictionKillerService:
    
    TECHNIQUE_INFO = {
        'deep_breathing': {
            'name': 'Deep Breathing',
            'description': 'Practice 4-7-8 breathing: inhale for 4 seconds, hold for 7, exhale for 8.',
            'duration': '2-5 minutes'
        },
        'progressive_muscle': {
            'name': 'Progressive Muscle Relaxation',
            'description': 'Tense and release muscle groups to reduce physical tension.',
            'duration': '10-15 minutes'
        },
        'mindfulness': {
            'name': 'Mindfulness Meditation',
            'description': 'Focus on the present moment without judgment.',
            'duration': '5-20 minutes'
        },
        'urge_surfing': {
            'name': 'Urge Surfing',
            'description': 'Ride the wave of the craving without acting on it. Cravings peak and pass.',
            'duration': '10-30 minutes'
        },
        'cognitive_reframing': {
            'name': 'Cognitive Reframing',
            'description': 'Challenge and change negative thought patterns about your addiction.',
            'duration': '5-10 minutes'
        },
        'physical_activity': {
            'name': 'Physical Activity',
            'description': 'Exercise to release endorphins and distract from cravings.',
            'duration': '15-30 minutes'
        },
        'gratitude_practice': {
            'name': 'Gratitude Practice',
            'description': 'List things you are grateful for to shift focus from cravings.',
            'duration': '5 minutes'
        },
        'connection': {
            'name': 'Social Connection',
            'description': 'Reach out to a support person or sponsor.',
            'duration': 'As needed'
        },
        'journaling': {
            'name': 'Urge Journaling',
            'description': 'Write about your urges, triggers, and coping strategies.',
            'duration': '10-15 minutes'
        },
        'visualization': {
            'name': 'Visualization',
            'description': 'Visualize yourself successfully overcoming the craving.',
            'duration': '5-10 minutes'
        }
    }
    
    @staticmethod
    def create_killer(user_id, name, technique, target_addiction=None, notes=None):
        killer = AddictionKiller(
            user_id=user_id,
            name=name,
            technique=technique,
            target_addiction=target_addiction,
            notes=notes
        )
        db.session.add(killer)
        db.session.commit()
        return killer
    
    @staticmethod
    def get_killer(user_id, killer_id):
        return AddictionKiller.query.filter_by(id=killer_id, user_id=user_id).first()
    
    @staticmethod
    def get_user_killers(user_id, active_only=True):
        query = AddictionKiller.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(AddictionKiller.name.asc()).all()
    
    @staticmethod
    def use_killer(user_id, killer_id, craving_intensity, notes=None):
        killer = AddictionKillerService.get_killer(user_id, killer_id)
        if not killer:
            return None
        
        session = AddictionSession(
            user_id=user_id,
            killer_id=killer_id,
            craving_intensity=craving_intensity,
            notes=notes
        )
        
        killer.times_used += 1
        
        db.session.add(session)
        db.session.commit()
        return session
    
    @staticmethod
    def update_session_after_intensity(session_id, user_id, after_intensity):
        session = AddictionSession.query.filter_by(id=session_id, user_id=user_id).first()
        if session:
            session.after_intensity = after_intensity
            db.session.commit()
        return session
    
    @staticmethod
    def rate_effectiveness(killer_id, user_id, rating):
        killer = AddictionKillerService.get_killer(user_id, killer_id)
        if killer:
            killer.effectiveness_rating = rating
            db.session.commit()
        return killer
    
    @staticmethod
    def update_killer(killer_id, user_id, **kwargs):
        killer = AddictionKillerService.get_killer(user_id, killer_id)
        if not killer:
            return None
        for key, value in kwargs.items():
            if hasattr(killer, key):
                setattr(killer, key, value)
        killer.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return killer
    
    @staticmethod
    def delete_killer(killer_id, user_id):
        killer = AddictionKillerService.get_killer(user_id, killer_id)
        if not killer:
            return False
        db.session.delete(killer)
        db.session.commit()
        return True
    
    @staticmethod
    def get_killer_sessions(user_id, killer_id, limit=20):
        return AddictionSession.query.filter_by(user_id=user_id, killer_id=killer_id)\
            .order_by(AddictionSession.completed_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_most_used_killers(user_id, limit=5):
        return AddictionKiller.query.filter_by(user_id=user_id)\
            .order_by(AddictionKiller.times_used.desc()).limit(limit).all()
    
    @staticmethod
    def get_most_effective_killers(user_id, limit=5):
        return AddictionKiller.query.filter(
            AddictionKiller.user_id == user_id,
            AddictionKiller.effectiveness_rating.isnot(None)
        ).order_by(AddictionKiller.effectiveness_rating.desc()).limit(limit).all()
    
    @staticmethod
    def get_technique_info(technique):
        return AddictionKillerService.TECHNIQUE_INFO.get(technique)
