from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from core import db

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False, index=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Application content
    cover_letter = db.Column(db.Text, nullable=True)
    resume_path = db.Column(db.String(255), nullable=True)
    portfolio_url = db.Column(db.String(255), nullable=True)
    
    # Additional information
    expected_salary = db.Column(db.Integer, nullable=True)
    available_from = db.Column(db.Date, nullable=True)
    notice_period = db.Column(db.String(50), nullable=True)  # immediate, 2weeks, 1month, etc.
    
    # Contact preferences
    preferred_contact_method = db.Column(db.String(20), default='telegram')  # telegram, email, phone
    contact_time_preference = db.Column(db.String(50), nullable=True)  # morning, afternoon, evening
    
    # Status tracking
    status = db.Column(db.String(20), default='pending', index=True)  # pending, reviewed, accepted, rejected, withdrawn
    employer_notes = db.Column(db.Text, nullable=True)
    applicant_notes = db.Column(db.Text, nullable=True)
    
    # Interview information
    interview_scheduled = db.Column(db.Boolean, default=False)
    interview_date = db.Column(db.DateTime, nullable=True)
    interview_type = db.Column(db.String(20), nullable=True)  # phone, video, in-person
    interview_notes = db.Column(db.Text, nullable=True)
    
    # Feedback and rating
    employer_rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    employer_feedback = db.Column(db.Text, nullable=True)
    applicant_rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    applicant_feedback = db.Column(db.Text, nullable=True)
    
    # Metadata
    source = db.Column(db.String(50), default='telegram')  # telegram, website, api
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    responded_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Application {self.id} for Job {self.job_id}>'
    
    def get_status_display(self):
        """Возвращает статус в читаемом формате"""
        status_map = {
            'pending': '⏳ На рассмотрении',
            'reviewed': '👀 Просмотрено',
            'accepted': '✅ Принято',
            'rejected': '❌ Отклонено',
            'withdrawn': '🚫 Отозвано',
            'interview': '🎯 Собеседование',
            'offer': '💼 Предложение'
        }
        return status_map.get(self.status, self.status)
    
    def get_status_emoji(self):
        """Возвращает эмодзи для статуса"""
        emoji_map = {
            'pending': '⏳',
            'reviewed': '👀',
            'accepted': '✅',
            'rejected': '❌',
            'withdrawn': '🚫',
            'interview': '🎯',
            'offer': '💼'
        }
        return emoji_map.get(self.status, '📄')
    
    def update_status(self, new_status, notes=None):
        """Обновляет статус отклика"""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status in ['reviewed', 'accepted', 'rejected'] and not self.reviewed_at:
            self.reviewed_at = datetime.utcnow()
        
        if new_status in ['accepted', 'rejected'] and not self.responded_at:
            self.responded_at = datetime.utcnow()
        
        if notes:
            self.employer_notes = notes
        
        db.session.commit()
        return old_status, new_status
    
    def schedule_interview(self, interview_date, interview_type='video', notes=None):
        """Планирует собеседование"""
        self.interview_scheduled = True
        self.interview_date = interview_date
        self.interview_type = interview_type
        if notes:
            self.interview_notes = notes
        self.status = 'interview'
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def get_notice_period_display(self):
        """Возвращает период уведомления в читаемом формате"""
        period_map = {
            'immediate': 'Немедленно',
            '1week': '1 неделя',
            '2weeks': '2 недели',
            '1month': '1 месяц',
            '2months': '2 месяца',
            '3months': '3 месяца'
        }
        return period_map.get(self.notice_period, self.notice_period)
    
    def get_contact_method_display(self):
        """Возвращает предпочитаемый способ связи в читаемом формате"""
        method_map = {
            'telegram': 'Telegram',
            'email': 'Email',
            'phone': 'Телефон',
            'whatsapp': 'WhatsApp'
        }
        return method_map.get(self.preferred_contact_method, self.preferred_contact_method)
    
    def get_time_since_application(self):
        """Возвращает время с момента подачи заявки"""
        if not self.created_at:
            return "Неизвестно"
        
        delta = datetime.utcnow() - self.created_at
        
        if delta.days > 0:
            return f"{delta.days} дн. назад"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} ч. назад"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} мин. назад"
        else:
            return "Только что"
    
    def to_dict(self):
        """Преобразует объект в словарь для JSON"""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'applicant_id': self.applicant_id,
            'cover_letter': self.cover_letter,
            'resume_path': self.resume_path,
            'portfolio_url': self.portfolio_url,
            'expected_salary': self.expected_salary,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'notice_period': self.notice_period,
            'notice_period_display': self.get_notice_period_display(),
            'preferred_contact_method': self.preferred_contact_method,
            'contact_method_display': self.get_contact_method_display(),
            'contact_time_preference': self.contact_time_preference,
            'status': self.status,
            'status_display': self.get_status_display(),
            'status_emoji': self.get_status_emoji(),
            'employer_notes': self.employer_notes,
            'applicant_notes': self.applicant_notes,
            'interview_scheduled': self.interview_scheduled,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'interview_type': self.interview_type,
            'interview_notes': self.interview_notes,
            'employer_rating': self.employer_rating,
            'employer_feedback': self.employer_feedback,
            'applicant_rating': self.applicant_rating,
            'applicant_feedback': self.applicant_feedback,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'time_since_application': self.get_time_since_application()
        }
    
    @staticmethod
    def get_by_job(job_id, status=None):
        """Получает отклики по вакансии"""
        query = Application.query.filter_by(job_id=job_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Application.created_at.desc()).all()
    
    @staticmethod
    def get_by_applicant(applicant_id, status=None):
        """Получает отклики соискателя"""
        query = Application.query.filter_by(applicant_id=applicant_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Application.created_at.desc()).all()
    
    @staticmethod
    def get_pending_applications(employer_id=None):
        """Получает отклики на рассмотрении"""
        query = Application.query.filter_by(status='pending')
        if employer_id:
            query = query.join(Job).filter(Job.employer_id == employer_id)
        return query.order_by(Application.created_at.asc()).all()
    
    @staticmethod
    def get_statistics(employer_id=None, days=30):
        """Получает статистику по откликам"""
        from datetime import timedelta
        
        since_date = datetime.utcnow() - timedelta(days=days)
        query = Application.query.filter(Application.created_at >= since_date)
        
        if employer_id:
            query = query.join(Job).filter(Job.employer_id == employer_id)
        
        total = query.count()
        pending = query.filter_by(status='pending').count()
        reviewed = query.filter_by(status='reviewed').count()
        accepted = query.filter_by(status='accepted').count()
        rejected = query.filter_by(status='rejected').count()
        
        return {
            'total': total,
            'pending': pending,
            'reviewed': reviewed,
            'accepted': accepted,
            'rejected': rejected,
            'response_rate': round((reviewed + accepted + rejected) / total * 100, 1) if total > 0 else 0,
            'acceptance_rate': round(accepted / total * 100, 1) if total > 0 else 0
        }
    
    @staticmethod
    def check_duplicate(job_id, applicant_id):
        """Проверяет, есть ли уже отклик от этого соискателя на эту вакансию"""
        return Application.query.filter_by(
            job_id=job_id,
            applicant_id=applicant_id
        ).first() is not None

