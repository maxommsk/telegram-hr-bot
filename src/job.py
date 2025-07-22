from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(100), nullable=False, index=True)
    location = db.Column(db.String(100), nullable=True, index=True)
    
    # Salary information
    salary_min = db.Column(db.Integer, nullable=True, index=True)
    salary_max = db.Column(db.Integer, nullable=True, index=True)
    salary_currency = db.Column(db.String(10), default='RUB')
    salary_period = db.Column(db.String(20), default='month')  # month, year, hour
    
    # Job details
    employment_type = db.Column(db.String(50), nullable=True, index=True)  # full-time, part-time, contract, remote
    experience_level = db.Column(db.String(50), nullable=True, index=True)  # junior, middle, senior, lead
    education_level = db.Column(db.String(50), nullable=True)  # bachelor, master, phd, none
    
    # Requirements and benefits
    requirements = db.Column(db.Text, nullable=True)
    responsibilities = db.Column(db.Text, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    skills_required = db.Column(db.Text, nullable=True)  # JSON string
    
    # Contact information
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    contact_person = db.Column(db.String(100), nullable=True)
    
    # External links
    company_website = db.Column(db.String(255), nullable=True)
    application_url = db.Column(db.String(255), nullable=True)
    
    # Job metadata
    category = db.Column(db.String(50), nullable=True, index=True)  # IT, Marketing, Sales, etc.
    tags = db.Column(db.Text, nullable=True)  # JSON string
    priority = db.Column(db.Integer, default=0)  # For featured jobs
    
    # Status and visibility
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_remote = db.Column(db.Boolean, default=False, index=True)
    is_urgent = db.Column(db.Boolean, default=False)
    
    # Statistics
    views_count = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    
    # Dates
    expires_at = db.Column(db.DateTime, nullable=True, index=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    employer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Relationships
    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Job {self.title} at {self.company}>'
    
    def is_expired(self):
        """Проверяет, истек ли срок вакансии"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def get_salary_range(self):
        """Возвращает диапазон зарплаты в читаемом формате"""
        if self.salary_min and self.salary_max:
            return f"{self.salary_min:,} - {self.salary_max:,} {self.salary_currency}"
        elif self.salary_min:
            return f"от {self.salary_min:,} {self.salary_currency}"
        elif self.salary_max:
            return f"до {self.salary_max:,} {self.salary_currency}"
        else:
            return "Зарплата не указана"
    
    def increment_views(self):
        """Увеличивает счетчик просмотров"""
        self.views_count += 1
        db.session.commit()
    
    def increment_applications(self):
        """Увеличивает счетчик откликов"""
        self.applications_count += 1
        db.session.commit()
    
    def get_short_description(self, max_length=200):
        """Возвращает краткое описание вакансии"""
        if len(self.description) <= max_length:
            return self.description
        return self.description[:max_length] + "..."
    
    def get_employment_type_display(self):
        """Возвращает тип занятости в читаемом формате"""
        employment_types = {
            'full-time': 'Полная занятость',
            'part-time': 'Частичная занятость',
            'contract': 'Контракт',
            'remote': 'Удаленная работа',
            'freelance': 'Фриланс',
            'internship': 'Стажировка'
        }
        return employment_types.get(self.employment_type, self.employment_type)
    
    def get_experience_level_display(self):
        """Возвращает уровень опыта в читаемом формате"""
        experience_levels = {
            'junior': 'Junior (до 1 года)',
            'middle': 'Middle (1-3 года)',
            'senior': 'Senior (3-5 лет)',
            'lead': 'Lead (5+ лет)',
            'intern': 'Стажер (без опыта)'
        }
        return experience_levels.get(self.experience_level, self.experience_level)
    
    def to_dict(self):
        """Преобразует объект в словарь для JSON"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'company': self.company,
            'location': self.location,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_currency': self.salary_currency,
            'salary_period': self.salary_period,
            'salary_range': self.get_salary_range(),
            'employment_type': self.employment_type,
            'employment_type_display': self.get_employment_type_display(),
            'experience_level': self.experience_level,
            'experience_level_display': self.get_experience_level_display(),
            'education_level': self.education_level,
            'requirements': self.requirements,
            'responsibilities': self.responsibilities,
            'benefits': self.benefits,
            'skills_required': self.skills_required,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'contact_person': self.contact_person,
            'company_website': self.company_website,
            'application_url': self.application_url,
            'category': self.category,
            'tags': self.tags,
            'priority': self.priority,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'is_remote': self.is_remote,
            'is_urgent': self.is_urgent,
            'views_count': self.views_count,
            'applications_count': self.applications_count,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'employer_id': self.employer_id,
            'is_expired': self.is_expired()
        }
    
    @staticmethod
    def search(query=None, location=None, salary_min=None, employment_type=None, 
               experience_level=None, category=None, is_remote=None, page=1, per_page=10):
        """Поиск вакансий с фильтрами"""
        jobs_query = Job.query.filter(Job.is_active == True)
        
        if query:
            jobs_query = jobs_query.filter(
                db.or_(
                    Job.title.ilike(f'%{query}%'),
                    Job.description.ilike(f'%{query}%'),
                    Job.company.ilike(f'%{query}%')
                )
            )
        
        if location:
            jobs_query = jobs_query.filter(Job.location.ilike(f'%{location}%'))
        
        if salary_min:
            jobs_query = jobs_query.filter(Job.salary_min >= salary_min)
        
        if employment_type:
            jobs_query = jobs_query.filter(Job.employment_type == employment_type)
        
        if experience_level:
            jobs_query = jobs_query.filter(Job.experience_level == experience_level)
        
        if category:
            jobs_query = jobs_query.filter(Job.category == category)
        
        if is_remote is not None:
            jobs_query = jobs_query.filter(Job.is_remote == is_remote)
        
        # Сортировка: сначала срочные, потом по дате публикации
        jobs_query = jobs_query.order_by(
            Job.is_urgent.desc(),
            Job.is_featured.desc(),
            Job.published_at.desc()
        )
        
        return jobs_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @staticmethod
    def get_active_jobs(employer_id=None):
        """Получает активные вакансии"""
        query = Job.query.filter(Job.is_active == True)
        if employer_id:
            query = query.filter(Job.employer_id == employer_id)
        return query.order_by(Job.published_at.desc()).all()
    
    @staticmethod
    def get_featured_jobs(limit=5):
        """Получает рекомендуемые вакансии"""
        return Job.query.filter(
            Job.is_active == True,
            Job.is_featured == True
        ).order_by(Job.published_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_recent_jobs(limit=10):
        """Получает последние вакансии"""
        return Job.query.filter(
            Job.is_active == True
        ).order_by(Job.published_at.desc()).limit(limit).all()

