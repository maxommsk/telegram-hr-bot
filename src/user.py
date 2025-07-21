from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), nullable=True, index=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    phone_number = db.Column(db.String(20), nullable=True)
    
    # User type: 'employer' or 'jobseeker'
    user_type = db.Column(db.String(20), nullable=False, default='jobseeker', index=True)
    
    # Profile information
    company = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)  # JSON string
    experience_years = db.Column(db.Integer, nullable=True)
    education = db.Column(db.Text, nullable=True)
    
    # Resume and portfolio
    resume_path = db.Column(db.String(255), nullable=True)
    portfolio_url = db.Column(db.String(255), nullable=True)
    
    # Settings
    notification_enabled = db.Column(db.Boolean, default=True)
    language = db.Column(db.String(10), default='ru')
    timezone = db.Column(db.String(50), default='Europe/Moscow')
    
    # Status and metadata
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='employer', lazy=True, foreign_keys='Job.employer_id')
    applications = db.relationship('Application', backref='applicant', lazy=True, foreign_keys='Application.applicant_id')
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username or self.telegram_id}>'
    
    def is_employer(self):
        """Проверяет, является ли пользователь работодателем"""
        return self.user_type == 'employer'
    
    def is_jobseeker(self):
        """Проверяет, является ли пользователь соискателем"""
        return self.user_type == 'jobseeker'
    
    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return self.username
        else:
            return f"User {self.telegram_id}"
    
    def update_last_activity(self):
        """Обновляет время последней активности"""
        self.last_activity = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Преобразует объект в словарь для JSON"""
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'user_type': self.user_type,
            'company': self.company,
            'position': self.position,
            'location': self.location,
            'bio': self.bio,
            'skills': self.skills,
            'experience_years': self.experience_years,
            'education': self.education,
            'resume_path': self.resume_path,
            'portfolio_url': self.portfolio_url,
            'notification_enabled': self.notification_enabled,
            'language': self.language,
            'timezone': self.timezone,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def find_by_telegram_id(telegram_id):
        """Находит пользователя по Telegram ID"""
        return User.query.filter_by(telegram_id=telegram_id).first()
    
    @staticmethod
    def create_from_telegram(telegram_user, user_type='jobseeker'):
        """Создает пользователя из объекта Telegram User"""
        user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            user_type=user_type
        )
        db.session.add(user)
        db.session.commit()
        return user
