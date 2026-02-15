from datetime import datetime, timezone
from app import db
from app.models import RelapseEvent


class RelapseService:
    
    @staticmethod
    def create_relapse(user_id, occurred_at, trigger_type, severity, notes=None):
        if not RelapseEvent.validate_trigger_type(trigger_type):
            raise ValueError(f'Invalid trigger type: {trigger_type}')
        
        if not RelapseEvent.validate_severity(severity):
            raise ValueError('Severity must be between 1 and 10')
        
        if occurred_at is None:
            occurred_at = datetime.now(timezone.utc)
        
        relapse = RelapseEvent(
            user_id=user_id,
            occurred_at=occurred_at,
            trigger_type=trigger_type,
            severity=severity,
            notes=notes
        )
        
        db.session.add(relapse)
        db.session.commit()
        
        return relapse
    
    @staticmethod
    def get_relapse_by_id(relapse_id):
        return RelapseEvent.query.get(relapse_id)
    
    @staticmethod
    def get_user_relapses(user_id, limit=None, order_desc=True):
        query = RelapseEvent.query.filter_by(user_id=user_id)
        
        if order_desc:
            query = query.order_by(RelapseEvent.occurred_at.desc())
        else:
            query = query.order_by(RelapseEvent.occurred_at.asc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def update_relapse(relapse_id, **kwargs):
        relapse = RelapseEvent.query.get(relapse_id)
        if not relapse:
            return None
        
        allowed_fields = ['trigger_type', 'severity', 'notes', 'occurred_at']
        for field in allowed_fields:
            if field in kwargs:
                if field == 'trigger_type' and not RelapseEvent.validate_trigger_type(kwargs[field]):
                    raise ValueError(f'Invalid trigger type: {kwargs[field]}')
                if field == 'severity' and not RelapseEvent.validate_severity(kwargs[field]):
                    raise ValueError('Severity must be between 1 and 10')
                setattr(relapse, field, kwargs[field])
        
        db.session.commit()
        
        return relapse
    
    @staticmethod
    def delete_relapse(relapse_id):
        relapse = RelapseEvent.query.get(relapse_id)
        if not relapse:
            return False
        
        db.session.delete(relapse)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_relapse_stats(user_id):
        relapses = RelapseEvent.query.filter_by(user_id=user_id).all()
        
        if not relapses:
            return {
                'total_count': 0,
                'avg_severity': 0,
                'trigger_breakdown': {}
            }
        
        total_count = len(relapses)
        severities = [r.severity for r in relapses if r.severity is not None]
        avg_severity = sum(severities) / len(severities) if severities else 0
        
        trigger_breakdown = {}
        for r in relapses:
            if r.trigger_type:
                trigger_breakdown[r.trigger_type] = trigger_breakdown.get(r.trigger_type, 0) + 1
        
        return {
            'total_count': total_count,
            'avg_severity': round(avg_severity, 2),
            'trigger_breakdown': trigger_breakdown
        }
    
    @staticmethod
    def get_recent_relapses_days(user_id, days=30):
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        return RelapseEvent.query.filter(
            RelapseEvent.user_id == user_id,
            RelapseEvent.occurred_at >= cutoff
        ).order_by(RelapseEvent.occurred_at.desc()).all()
