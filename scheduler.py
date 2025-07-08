import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import List

from user import db
from job import Job
from subscription import Subscription

logger = logging.getLogger(__name__)

class NotificationScheduler:
    """Планировщик уведомлений о новых вакансиях"""
    
    def __init__(self, telegram_bot, flask_app):
        self.bot = telegram_bot
        self.app = flask_app
        self.running = False
        self.setup_schedule()
        
        logger.info("NotificationScheduler инициализирован")
    
    def setup_schedule(self):
        """Настройка расписания уведомлений"""
        # Проверка немедленных уведомлений каждые 5 минут
        schedule.every(5).minutes.do(self.send_immediate_notifications)
        
        # Ежедневные уведомления в 9:00
        schedule.every().day.at("09:00").do(self.send_daily_notifications)
        
        # Еженедельные уведомления по понедельникам в 10:00
        schedule.every().monday.at("10:00").do(self.send_weekly_notifications)
        
        # Очистка старых данных каждый день в 2:00
        schedule.every().day.at("02:00").do(self.cleanup_old_data)
    
    def start(self):
        """Запускает планировщик"""
        self.running = True
        
        def run_scheduler():
            while self.running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Проверяем каждую минуту
                except Exception as e:
                    logger.error(f"Ошибка в планировщике: {e}")
                    time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("Планировщик уведомлений запущен")
    
    def stop(self):
        """Останавливает планировщик"""
        self.running = False
        logger.info("Планировщик уведомлений остановлен")
    
    def send_immediate_notifications(self):
        """Отправляет немедленные уведомления"""
        with self.app.app_context():
            try:
                # Получаем подписки с немедленными уведомлениями
                subscriptions = Subscription.query.filter_by(
                    frequency='immediate',
                    is_active=True,
                    is_paused=False
                ).all()
                
                for subscription in subscriptions:
                    self.process_subscription(subscription)
                    
            except Exception as e:
                logger.error(f"Ошибка при отправке немедленных уведомлений: {e}")
    
    def send_daily_notifications(self):
        """Отправляет ежедневные уведомления"""
        with self.app.app_context():
            try:
                subscriptions = Subscription.query.filter_by(
                    frequency='daily',
                    is_active=True,
                    is_paused=False
                ).all()
                
                for subscription in subscriptions:
                    if subscription.should_send_notification():
                        self.process_subscription(subscription)
                        
            except Exception as e:
                logger.error(f"Ошибка при отправке ежедневных уведомлений: {e}")
    
    def send_weekly_notifications(self):
        """Отправляет еженедельные уведомления"""
        with self.app.app_context():
            try:
                subscriptions = Subscription.query.filter_by(
                    frequency='weekly',
                    is_active=True,
                    is_paused=False
                ).all()
                
                for subscription in subscriptions:
                    if subscription.should_send_notification():
                        self.process_subscription(subscription)
                        
            except Exception as e:
                logger.error(f"Ошибка при отправке еженедельных уведомлений: {e}")
    
    def process_subscription(self, subscription: Subscription):
        """Обрабатывает подписку и отправляет уведомления"""
        try:
            # Получаем критерии поиска
            criteria = subscription.get_criteria_dict()
            
            # Определяем период поиска
            if subscription.frequency == 'immediate':
                since_date = subscription.last_notification_sent or (datetime.utcnow() - timedelta(hours=1))
            elif subscription.frequency == 'daily':
                since_date = datetime.utcnow() - timedelta(days=1)
            else:  # weekly
                since_date = datetime.utcnow() - timedelta(days=7)
            
            # Ищем новые вакансии
            jobs = self.find_matching_jobs(criteria, since_date, subscription)
            
            if jobs:
                self.send_notification_to_user(subscription, jobs)
                subscription.mark_notification_sent(len(jobs))
                
        except Exception as e:
            logger.error(f"Ошибка при обработке подписки {subscription.id}: {e}")
    
    def find_matching_jobs(self, criteria: dict, since_date: datetime, subscription: Subscription) -> List[Job]:
        """Находит вакансии, соответствующие критериям"""
        query = Job.query.filter(
            Job.is_active == True,
            Job.published_at >= since_date
        )
        
        # Применяем фильтры из критериев
        if 'keywords' in criteria:
            keywords = criteria['keywords']
            query = query.filter(
                db.or_(
                    Job.title.ilike(f'%{keywords}%'),
                    Job.description.ilike(f'%{keywords}%')
                )
            )
        
        if 'location' in criteria:
            location = criteria['location']
            query = query.filter(Job.location.ilike(f'%{location}%'))
        
        if 'company' in criteria:
            company = criteria['company']
            query = query.filter(Job.company.ilike(f'%{company}%'))
        
        # Применяем дополнительные фильтры
        if subscription.min_salary:
            query = query.filter(Job.salary_min >= subscription.min_salary)
        
        if subscription.only_remote:
            query = query.filter(Job.is_remote == True)
        
        if subscription.only_featured:
            query = query.filter(Job.is_featured == True)
        
        # Исключаем по черному списку компаний
        company_blacklist = subscription.get_company_blacklist_list()
        if company_blacklist:
            for company in company_blacklist:
                query = query.filter(~Job.company.ilike(f'%{company}%'))
        
        # Исключаем по ключевым словам
        exclude_keywords = subscription.get_exclude_keywords_list()
        if exclude_keywords:
            for keyword in exclude_keywords:
                query = query.filter(
                    ~db.and_(
                        Job.title.ilike(f'%{keyword}%'),
                        Job.description.ilike(f'%{keyword}%')
                    )
                )
        
        # Ограничиваем количество результатов
        max_jobs = subscription.max_notifications_per_day or 10
        
        return query.order_by(Job.published_at.desc()).limit(max_jobs).all()
    
    def send_notification_to_user(self, subscription: Subscription, jobs: List[Job]):
        """Отправляет уведомление пользователю"""
        try:
            user = subscription.user
            
            if len(jobs) == 1:
                # Одна вакансия - подробное уведомление
                job = jobs[0]
                text = f"🔔 <b>Новая вакансия по подписке \"{subscription.name}\"</b>\n\n"
                text += f"💼 <b>{job.title}</b>\n"
                text += f"🏢 {job.company}\n"
                text += f"📍 {job.location or 'Не указано'}\n"
                text += f"💰 {job.get_salary_range()}\n\n"
                text += f"📝 {job.get_short_description(150)}\n\n"
                text += f"🕒 Опубликовано: {job.published_at.strftime('%d.%m.%Y %H:%M')}"
                
                from telebot import types
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("👀 Подробнее", callback_data=f"view_job_{job.id}"),
                    types.InlineKeyboardButton("📝 Откликнуться", callback_data=f"apply_job_{job.id}")
                )
                markup.add(
                    types.InlineKeyboardButton("⚙️ Настроить подписку", callback_data=f"edit_subscription_{subscription.id}")
                )
                
            else:
                # Несколько вакансий - краткий список
                text = f"🔔 <b>Найдено {len(jobs)} новых вакансий по подписке \"{subscription.name}\"</b>\n\n"
                
                for i, job in enumerate(jobs[:5], 1):
                    text += f"{i}. <b>{job.title}</b> в {job.company}\n"
                    text += f"   📍 {job.location or 'Не указано'} | 💰 {job.get_salary_range()}\n\n"
                
                if len(jobs) > 5:
                    text += f"... и еще {len(jobs) - 5} вакансий\n\n"
                
                from telebot import types
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("📋 Посмотреть все", callback_data="all_jobs"),
                    types.InlineKeyboardButton("🔍 Поиск", callback_data="search_jobs")
                )
                markup.add(
                    types.InlineKeyboardButton("⚙️ Настроить подписку", callback_data=f"edit_subscription_{subscription.id}")
                )
            
            self.bot.bot.send_message(
                user.telegram_id,
                text,
                parse_mode='HTML',
                reply_markup=markup
            )
            
            logger.info(f"Отправлено уведомление пользователю {user.telegram_id} о {len(jobs)} вакансиях")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления пользователю {subscription.user_id}: {e}")
    
    def cleanup_old_data(self):
        """Очищает старые данные"""
        with self.app.app_context():
            try:
                # Удаляем истекшие подписки
                expired_date = datetime.utcnow()
                expired_subscriptions = Subscription.query.filter(
                    Subscription.expires_at < expired_date
                ).all()
                
                for subscription in expired_subscriptions:
                    subscription.deactivate()
                
                logger.info(f"Деактивировано {len(expired_subscriptions)} истекших подписок")
                
                # Деактивируем старые вакансии (старше 90 дней без активности)
                old_date = datetime.utcnow() - timedelta(days=90)
                old_jobs = Job.query.filter(
                    Job.is_active == True,
                    Job.published_at < old_date,
                    Job.applications_count == 0
                ).all()
                
                for job in old_jobs:
                    job.is_active = False
                
                db.session.commit()
                logger.info(f"Деактивировано {len(old_jobs)} старых вакансий")
                
            except Exception as e:
                logger.error(f"Ошибка при очистке старых данных: {e}")
    
    def send_test_notification(self, user_id: int, message: str):
        """Отправляет тестовое уведомление"""
        try:
            self.bot.bot.send_message(user_id, f"🧪 Тест: {message}")
            logger.info(f"Отправлено тестовое уведомление пользователю {user_id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке тестового уведомления: {e}")
    
    def get_statistics(self) -> dict:
        """Возвращает статистику планировщика"""
        with self.app.app_context():
            try:
                total_subscriptions = Subscription.query.count()
                active_subscriptions = Subscription.query.filter_by(
                    is_active=True,
                    is_paused=False
                ).count()
                
                immediate_subs = Subscription.query.filter_by(
                    frequency='immediate',
                    is_active=True,
                    is_paused=False
                ).count()
                
                daily_subs = Subscription.query.filter_by(
                    frequency='daily',
                    is_active=True,
                    is_paused=False
                ).count()
                
                weekly_subs = Subscription.query.filter_by(
                    frequency='weekly',
                    is_active=True,
                    is_paused=False
                ).count()
                
                return {
                    'total_subscriptions': total_subscriptions,
                    'active_subscriptions': active_subscriptions,
                    'immediate_subscriptions': immediate_subs,
                    'daily_subscriptions': daily_subs,
                    'weekly_subscriptions': weekly_subs,
                    'scheduler_running': self.running
                }
                
            except Exception as e:
                logger.error(f"Ошибка при получении статистики планировщика: {e}")
                return {}

