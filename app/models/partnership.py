import uuid
from datetime import datetime, timezone
from app import db


class Partnership(db.Model):
    __tablename__ = 'partnerships'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user1_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    user2_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])
    
    def __repr__(self):
        return f'<Partnership {self.user1_id} - {self.user2_id}>'
    
    def get_partner(self, user_id):
        if self.user1_id == user_id:
            return self.user2
        return self.user1


class SharedGoal(db.Model):
    __tablename__ = 'shared_goals'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partnership_id = db.Column(db.String(36), db.ForeignKey('partnerships.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    frequency = db.Column(db.String(20), nullable=False, default='daily')
    category = db.Column(db.String(50), nullable=True)
    target_date = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    partnership = db.relationship('Partnership', backref=db.backref('shared_goals', lazy='dynamic'))
    
    def __repr__(self):
        return f'<SharedGoal {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'partnership_id': self.partnership_id,
            'title': self.title,
            'description': self.description,
            'frequency': self.frequency,
            'category': self.category,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'milestones': [m.to_dict() for m in self.milestones]
        }


class GoalMilestone(db.Model):
    __tablename__ = 'goal_milestones'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id = db.Column(db.String(36), db.ForeignKey('shared_goals.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<GoalMilestone {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'goal_id': self.goal_id,
            'title': self.title,
            'order': self.order,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class PartnerMessage(db.Model):
    __tablename__ = 'partner_messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partnership_id = db.Column(db.String(36), db.ForeignKey('partnerships.id'), nullable=False, index=True)
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    partnership = db.relationship('Partnership', backref='messages')
    sender = db.relationship('User')
    
    def __repr__(self):
        return f'<PartnerMessage {self.id}>'


class SharedGoalProgress(db.Model):
    __tablename__ = 'shared_goal_progress'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shared_goal_id = db.Column(db.String(36), db.ForeignKey('shared_goals.id'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    progress = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    shared_goal = db.relationship('SharedGoal', backref='progress_entries')
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<SharedGoalProgress goal={self.shared_goal_id} user={self.user_id}>'
