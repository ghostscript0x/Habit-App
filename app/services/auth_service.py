from datetime import datetime, timezone
from app import db, bcrypt
from app.models import User


class AuthService:
    
    @staticmethod
    def create_user(email, username, password):
        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            if existing_user.email == email:
                raise ValueError('Email already registered')
            if existing_user.username == username:
                raise ValueError('Username already taken')
        
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        user = User(
            email=email,
            username=username,
            password_hash=password_hash
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def authenticate(email, password):
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if bcrypt.check_password_hash(user.password_hash, password):
            return user
        
        return None
    
    @staticmethod
    def update_password(user, new_password):
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all_users():
        return User.query.all()
    
    @staticmethod
    def toggle_user_active(user):
        user.is_active = not user.is_active
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return user
