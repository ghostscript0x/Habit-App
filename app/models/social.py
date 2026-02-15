import uuid
from datetime import datetime, timezone
from app import db


class PreventionPlan(db.Model):
    __tablename__ = 'prevention_plans'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    warning_signs = db.Column(db.Text, nullable=True)
    coping_strategies = db.Column(db.Text, nullable=True)
    support_people = db.Column(db.Text, nullable=True)
    activities = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref='prevention_plans')
    
    def __repr__(self):
        return f'<PreventionPlan {self.title}>'


class UserReport(db.Model):
    __tablename__ = 'user_reports'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reporter_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    reported_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    reason = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    resolved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    reporter = db.relationship('User', foreign_keys=[reporter_id])
    reported_user = db.relationship('User', foreign_keys=[reported_user_id])
    
    def __repr__(self):
        return f'<UserReport {self.id}>'


class CommunityPost(db.Model):
    __tablename__ = 'community_posts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    is_anonymous = db.Column(db.Boolean, default=True)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref='community_posts')
    likes = db.relationship('CommunityPostLike', backref='post', cascade='all, delete-orphan')
    comments = db.relationship('CommunityComment', backref='post', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CommunityPost {self.id}>'


class CommunityPostLike(db.Model):
    __tablename__ = 'community_post_likes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = db.Column(db.String(36), db.ForeignKey('community_posts.id'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<CommunityPostLike {self.id}>'


class CommunityComment(db.Model):
    __tablename__ = 'community_comments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = db.Column(db.String(36), db.ForeignKey('community_posts.id'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<CommunityComment {self.id}>'
