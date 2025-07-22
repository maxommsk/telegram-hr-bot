from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db
import json

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Subscription details
    name = db.Column(db.String(100), nullable=False)  # User-friendly name
    subscription_type = db.Column(db.String(50), nullable=False, index=True)  # keywords, location, salary, company, category
    
    # Search criteria (JSON format for flexibility)
    criteria = db.Column(db.Text, nullable=False)  # JSON string with search parameters
    
    # Notification settings
    frequency = db.Column(db.String(20), nullable=False, default='daily')  # immediate, daily, weekly
    notification_time = db.Column(db.Time, nullable=True)  # Specific time for daily/weekly notifications
    notification_days = db.Column(db.String(20), nullable=True)  # For weekly: monday, tuesday, etc.
    
    # Filters
    min_salary = db.Column(db.Integer, nullable=True)
    max_salary = db.Column(db.Integer, nullable=True)
    employment_types = db.Column(db.Text, nullable=True)  # JSON array
    experience_levels = db.Column(db.Text, nullable=True)  # JSON array
    locations = db.Column(db.Text, nullable=True)  # JSON array
    categories = db.Column(db.Text, nullable=True)  # JSON array
    
    # Advanced filters
    exclude_keywords = db.Column(db.Text, nullable=True)  # JSON array
    company_blacklist = db.Column(db.Text, nullable=True)  # JSON array
    only_remote = db.Column(db.Boolean, default=False)
    only_featured = db.Column(db.Boolean, default=False)
    
    # Notification tracking
    last_notification_sent = db.Column(db.DateTime, nullable=True)
    last_job_id_sent = db.Column(db.Integer, nullable=True)  # To avoid duplicate notifications
    total_notifications_sent = db.Column(db.Integer, default=0)
    total_jobs_found = db.Column(db.Integer, default=0)
    
    # Status and settings
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_paused = db.Column(db.Boolean, default=False)
    max_notifications_per_day = db.Column(db.Integer, default=10)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)  # Optional expiration
    
    def __repr__(self):
        return f'<Subscription {self.name} for User {self.user_id}>'
    
    def get_criteria_dict(self):
        """Возвращает критерии поиска как словарь"""
        try:
            return json.loads(self.criteria) if self.criteria else {}
        except json.JSONDecodeError:
            return {}
    
    def set_criteria_dict(self, criteria_dict):
        """Устанавливает критерии поиска из словаря"""
        self.criteria = json.dumps(criteria_dict, ensure_ascii=False)
    
    def get_employment_types_list(self):
        """Возвращает список типов занятости"""
        try:
            return json.loads(self.employment_types) if self.employment_types else []
        except json.JSONDecodeError:
            return []
    
    def set_employment_types_list(self, types_list):
        """Устанавливает список типов занятости"""
        self.employment_types = json.dumps(types_list, ensure_ascii=False)
    
    def get_experience_levels_list(self):
        """Возвращает список уровней опыта"""
        try:
            return json.loads(self.experience_levels) if self.experience_levels else []
        except json.JSONDecodeError:
            return []
    
    def set_experience_levels_list(self, levels_list):
        """Устанавливает список уровней опыта"""
        self.experience_levels = json.dumps(levels_list, ensure_ascii=False)
    
    def get_locations_list(self):
        """Возвращает список локаций"""
        try:
            return json.loads(self.locations) if self.locations else []
        except json.JSONDecodeError:
            return []
    
    def set_locations_list(self, locations_list):
        """Устанавливает список локаций"""
        self.locations = json.dumps(locations_list, ensure_ascii=False)
    
    def get_categories_list(self):
        """Возвращает список категорий"""
        try:
            return json.loads(self.categories) if self.categories else []
        except json.JSONDecodeError:
            return []
    
    def set_categories_list(self, categories_list):
        """Устанавливает список категорий"""
        self.categories = json.dumps(categories_list, ensure_ascii=False)
    
    def get_exclude_keywords_list(self):
        """Возвращает список исключаемых ключевых слов"""
        try:
            return json.loads(self.exclude_keywords) if self.exclude_keywords else []
        except json.JSONDecodeError:
            return []
    
    def set_exclude_keywords_list(self, keywords_list):
        """Устанавливает список исключаемых ключевых слов"""
        self.exclude_keywords = json.dumps(keywords_list, ensure_ascii=False)
    
    def get_company_blacklist_list(self):
        """Возвращает черный список компаний"""
        try:
            return json.loads(self.company_blacklist) if self.company_blacklist else []
        except json.JSONDecodeError:
            return []
    
    def set_company_blacklist_list(self, companies_list):
        """Устанавливает черный список компаний"""
        self.company_blacklist = json.dumps(companies_list, ensure_ascii=False)
    
    def get_frequency_display(self):
        """Возвращает частоту уведомлений в читаемом формате"""
        frequency_map = {
            'immediate': '🔔 Немедленно',
            'daily': '📅 Ежедневно',
            'weekly': '📆 Еженедельно',
            'disabled': '🔕 Отключено'
        }
        return frequency_map.get(self.frequency, self.frequency)
    
    def get_type_display(self):
        """Возвращает тип подписки в читаемом формате"""
        type_map = {
            'keywords': '🔍 По ключевым словам',
            'location': '📍 По местоположению',
            'salary': '💰 По зарплате',
            'company': '🏢 По компании',
            'category': '📂 По категории',
            'custom': '⚙️ Настраиваемая'
        }
        return type_map.get(self.subscription_type, self.subscription_type)
    
    def is_expired(self):
        """Проверяет, истекла ли подписка"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def should_send_notification(self):
        """Проверяет, нужно ли отправлять уведомление"""
        if not self.is_active or self.is_paused or self.is_expired():
            return False
        
        if self.frequency == 'immediate':
            return True
        
        if not self.last_notification_sent:
            return True
        
        now = datetime.utcnow()
        
        if self.frequency == 'daily':
            # Проверяем, прошел ли день с последнего уведомления
            return (now - self.last_notification_sent).days >= 1
        
        elif self.frequency == 'weekly':
            # Проверяем, прошла ли неделя с последнего уведомления
            return (now - self.last_notification_sent).days >= 7
        
        return False
    
    def mark_notification_sent(self, jobs_count=0):
        """Отмечает, что уведомление было отправлено"""
        self.last_notification_sent = datetime.utcnow()
        self.total_notifications_sent += 1
        self.total_jobs_found += jobs_count
        db.session.commit()
    
    def pause(self):
        """Приостанавливает подписку"""
        self.is_paused = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def resume(self):
        """Возобновляет подписку"""
        self.is_paused = False
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def deactivate(self):
        """Деактивирует подписку"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def get_summary(self):
        """Возвращает краткое описание подписки"""
        criteria = self.get_criteria_dict()
        summary_parts = []
        
        if self.subscription_type == 'keywords' and 'keywords' in criteria:
            summary_parts.append(f"Ключевые слова: {criteria['keywords']}")
        
        if self.subscription_type == 'location' and 'location' in criteria:
            summary_parts.append(f"Местоположение: {criteria['location']}")
        
        if self.subscription_type == 'company' and 'company' in criteria:
            summary_parts.append(f"Компания: {criteria['company']}")
        
        if self.min_salary:
            summary_parts.append(f"Зарплата от: {self.min_salary:,} руб.")
        
        if self.only_remote:
            summary_parts.append("Только удаленная работа")
        
        return "; ".join(summary_parts) if summary_parts else "Все вакансии"
    
    def to_dict(self):
        """Преобразует объект в словарь для JSON"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'subscription_type': self.subscription_type,
            'type_display': self.get_type_display(),
            'criteria': self.get_criteria_dict(),
            'frequency': self.frequency,
            'frequency_display': self.get_frequency_display(),
            'notification_time': self.notification_time.isoformat() if self.notification_time else None,
            'notification_days': self.notification_days,
            'min_salary': self.min_salary,
            'max_salary': self.max_salary,
            'employment_types': self.get_employment_types_list(),
            'experience_levels': self.get_experience_levels_list(),
            'locations': self.get_locations_list(),
            'categories': self.get_categories_list(),
            'exclude_keywords': self.get_exclude_keywords_list(),
            'company_blacklist': self.get_company_blacklist_list(),
            'only_remote': self.only_remote,
            'only_featured': self.only_featured,
            'last_notification_sent': self.last_notification_sent.isoformat() if self.last_notification_sent else None,
            'total_notifications_sent': self.total_notifications_sent,
            'total_jobs_found': self.total_jobs_found,
            'is_active': self.is_active,
            'is_paused': self.is_paused,
            'is_expired': self.is_expired(),
            'max_notifications_per_day': self.max_notifications_per_day,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'summary': self.get_summary()
        }
    
    @staticmethod
    def get_active_subscriptions(user_id=None):
        """Получает активные подписки"""
        query = Subscription.query.filter(
            Subscription.is_active == True,
            Subscription.is_paused == False
        )
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.order_by(Subscription.created_at.desc()).all()
    
    @staticmethod
    def get_due_notifications():
        """Получает подписки, для которых нужно отправить уведомления"""
        subscriptions = Subscription.get_active_subscriptions()
        return [sub for sub in subscriptions if sub.should_send_notification()]
    
    @staticmethod
    def create_keywords_subscription(user_id, name, keywords, frequency='daily'):
        """Создает подписку по ключевым словам"""
        criteria = {'keywords': keywords}
        subscription = Subscription(
            user_id=user_id,
            name=name,
            subscription_type='keywords',
            criteria=json.dumps(criteria, ensure_ascii=False),
            frequency=frequency
        )
        db.session.add(subscription)
        db.session.commit()
        return subscription
    
    @staticmethod
    def create_location_subscription(user_id, name, location, frequency='daily'):
        """Создает подписку по местоположению"""
        criteria = {'location': location}
        subscription = Subscription(
            user_id=user_id,
            name=name,
            subscription_type='location',
            criteria=json.dumps(criteria, ensure_ascii=False),
            frequency=frequency
        )
        db.session.add(subscription)
        db.session.commit()
        return subscription
    
    @staticmethod
    def create_salary_subscription(user_id, name, min_salary, frequency='daily'):
        """Создает подписку по зарплате"""
        criteria = {'min_salary': min_salary}
        subscription = Subscription(
            user_id=user_id,
            name=name,
            subscription_type='salary',
            criteria=json.dumps(criteria, ensure_ascii=False),
            frequency=frequency,
            min_salary=min_salary
        )
        db.session.add(subscription)
        db.session.commit()
        return subscription

