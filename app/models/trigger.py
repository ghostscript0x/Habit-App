import uuid
from datetime import datetime, timezone
from app import db


class Trigger(db.Model):
    __tablename__ = 'triggers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    times_encountered = db.Column(db.Integer, default=0)
    times_overcome = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Trigger user_id={self.user_id} name={self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'is_active': self.is_active,
            'times_encountered': self.times_encountered,
            'times_overcome': self.times_overcome,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
