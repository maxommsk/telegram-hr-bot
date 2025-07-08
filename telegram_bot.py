import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import telebot
from telebot import types
from flask import Flask, request

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from user import User, db
from job import Job
from application import Application
from subscription import Subscription

logger = logging.getLogger(__name__)

class TelegramHRBot:
    """Основной класс Telegram HR Bot с полным функционалом"""
    
    def __init__(self, token: str, flask_app: Flask):
        self.bot = telebot.TeleBot(token)
        self.app = flask_app
        self.user_states = {}  # Хранение состояний пользователей
        self.logger = logger  # Добавляем logger как атрибут класса
        self.setup_handlers()
        
        # Константы для пагинации
        self.JOBS_PER_PAGE = 5
        self.APPLICATIONS_PER_PAGE = 5
        
        logger.info("TelegramHRBot инициализирован")

    def get_or_create_user(self, telegram_user):
        """Получает или создает пользователя, возвращает telegram_id"""
        with self.app.app_context():
            user = User.query.filter_by(telegram_id=telegram_user.id).first()
            if not user:
                user = User(
                    telegram_id=telegram_user.id,
                    username=telegram_user.username,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name,
                    user_type='jobseeker',
                    is_active=True,
                    last_activity=datetime.utcnow()
                )
                db.session.add(user)
                db.session.commit()
                logger.info(f"Создан новый пользователь: {user.telegram_id}")
            else:
                user.last_activity = datetime.utcnow()
                db.session.commit()
            
            return telegram_user.id

    def get_user(self, telegram_id):
        """Получает пользователя по telegram_id в текущем контексте"""
        return User.query.filter_by(telegram_id=telegram_id).first()

    def handle_role_selection(self, call, role=None):
        """Обработка выбора роли пользователя"""
        try:
            telegram_id = call.from_user.id
            if role is None:
                role = call.data.split('_')[1]  # role_employer или role_jobseeker
            
            with self.app.app_context():
                # Получаем пользователя заново из базы
                user = User.query.filter_by(telegram_id=telegram_id).first()
                if user:
                    # Обновляем роль
                    user.user_type = role
                    db.session.commit()
                    
                    # Проверяем, что роль сохранилась
                    db.session.refresh(user)
                    print(f"DEBUG: Роль пользователя {telegram_id} изменена на {user.user_type}")
                    
                    if role == 'employer':
                        text = "🏢 Отлично! Вы зарегистрированы как работодатель.\n\nТеперь вы можете:\n• Создавать вакансии\n• Просматривать отклики\n• Управлять своими объявлениями"
                    else:
                        text = "👤 Отлично! Вы зарегистрированы как соискатель.\n\nТеперь вы можете:\n• Искать вакансии\n• Откликаться на предложения\n• Настроить уведомления"
                    
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
                    
                    self.bot.edit_message_text(
                        text=text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=markup
                    )
                    
        except Exception as e:
            self.logger.error(f"Ошибка в handle_role_selection: {e}")
    
    def show_role_switch(self, call):
        """Показывает меню смены роли"""
        try:
            text = "🔄 <b>Смена роли</b>\n\nВыберите новую роль:"
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("👔 Работодатель", callback_data="role_employer"),
                types.InlineKeyboardButton("💼 Соискатель", callback_data="role_jobseeker"),
                types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            )
            
            self.bot.edit_message_text(
                text=text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
        except Exception as e:
            self.logger.error(f"Ошибка в show_role_switch: {e}")
    
    def show_job_details(self, call, job_id):
        """Показывает детали вакансии"""
        try:
            telegram_id = call.from_user.id
            
            with self.app.app_context():
                job = Job.query.get(job_id)
                if not job:
                    self.bot.answer_callback_query(call.id, "Вакансия не найдена")
                    return
                
                user = self.get_user(telegram_id)
                
                text = f"💼 <b>{job.title}</b>\n\n"
                text += f"🏢 <b>Компания:</b> {job.company}\n"
                text += f"📍 <b>Местоположение:</b> {job.location or 'Не указано'}\n"
                
                # Формируем зарплату
                if job.salary_min and job.salary_max:
                    text += f"💰 <b>Зарплата:</b> {job.salary_min:,} - {job.salary_max:,} руб.\n"
                elif job.salary_min:
                    text += f"💰 <b>Зарплата:</b> от {job.salary_min:,} руб.\n"
                elif job.salary_max:
                    text += f"💰 <b>Зарплата:</b> до {job.salary_max:,} руб.\n"
                else:
                    text += f"💰 <b>Зарплата:</b> По договоренности\n"
                
                text += f"📅 <b>Опубликовано:</b> {job.created_at.strftime('%d.%m.%Y')}\n"
                
                # Считаем отклики
                applications_count = Application.query.filter_by(job_id=job_id).count()
                text += f"📨 <b>Откликов:</b> {applications_count}\n\n"
                text += f"📝 <b>Описание:</b>\n{job.description}"
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                
                if user and user.user_type == 'jobseeker':
                    # Проверяем, не откликался ли уже пользователь
                    existing_app = Application.query.filter_by(
                        job_id=job_id,
                        applicant_id=user.id
                    ).first()
                    
                    if not existing_app:
                        markup.add(
                            types.InlineKeyboardButton("📨 Откликнуться", callback_data=f"apply_job_{job_id}")
                        )
                    else:
                        markup.add(
                            types.InlineKeyboardButton("✅ Уже откликнулись", callback_data="already_applied")
                        )
                
                markup.add(
                    types.InlineKeyboardButton("⬅️ Назад к списку", callback_data="all_jobs"),
                    types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                )
                
                self.bot.edit_message_text(
                    text=text,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    parse_mode='HTML',
                    reply_markup=markup
                )
                
        except Exception as e:
            self.logger.error(f"Ошибка в show_job_details: {e}")
    
    def start_job_application(self, call, job_id):
        """Начинает процесс отклика на вакансию"""
        try:
            telegram_id = call.from_user.id
            
            with self.app.app_context():
                user = self.get_user(telegram_id)
                
                if not user or user.user_type != 'jobseeker':
                    self.bot.answer_callback_query(call.id, "Только соискатели могут откликаться на вакансии")
                    return
                
                # Проверяем, не откликался ли уже
                existing_app = Application.query.filter_by(
                    job_id=job_id,
                    applicant_id=user.id
                ).first()
                
                if existing_app:
                    self.bot.answer_callback_query(call.id, "Вы уже откликнулись на эту вакансию")
                    return
                
                job = Job.query.get(job_id)
                if not job:
                    self.bot.answer_callback_query(call.id, "Вакансия не найдена")
                    return
                
                # Создаем отклик
                application = Application(
                    job_id=job_id,
                    applicant_id=user.id,
                    cover_letter="Отклик через Telegram бота",
                    status='pending',
                    created_at=datetime.utcnow()
                )
                db.session.add(application)
                db.session.commit()
                
                text = f"✅ <b>Отклик отправлен!</b>\n\n"
                text += f"Вы откликнулись на вакансию:\n"
                text += f"💼 <b>{job.title}</b>\n"
                text += f"🏢 {job.company}\n\n"
                text += f"Работодатель получит уведомление о вашем отклике."
                
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("📨 Мои отклики", callback_data="my_applications"),
                    types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                )
                
                self.bot.edit_message_text(
                    text=text,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    parse_mode='HTML',
                    reply_markup=markup
                )
                
        except Exception as e:
            self.logger.error(f"Ошибка в start_job_application: {e}")
    
    def view_application_details(self, call, application_id):
        """Показывает детали отклика"""
        try:
            with self.app.app_context():
                application = Application.query.get(application_id)
                if not application:
                    self.bot.answer_callback_query(call.id, "Отклик не найден")
                    return
                
                job = Job.query.get(application.job_id)
                applicant = User.query.get(application.applicant_id)
                
                if not job or not applicant:
                    self.bot.answer_callback_query(call.id, "Данные не найдены")
                    return
                
                status_names = {
                    'pending': '⏳ Ожидает рассмотрения',
                    'accepted': '✅ Принят',
                    'rejected': '❌ Отклонен'
                }
                
                text = f"📨 <b>Детали отклика</b>\n\n"
                text += f"💼 <b>Вакансия:</b> {job.title}\n"
                text += f"🏢 <b>Компания:</b> {job.company}\n\n"
                text += f"👤 <b>Соискатель:</b> {applicant.get_full_name()}\n"
                if applicant.username:
                    text += f"📱 <b>Username:</b> @{applicant.username}\n"
                text += f"📅 <b>Дата отклика:</b> {application.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                text += f"📊 <b>Статус:</b> {status_names.get(application.status, application.status)}\n\n"
                
                if application.cover_letter:
                    text += f"📝 <b>Сопроводительное письмо:</b>\n{application.cover_letter}"
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                
                if application.status == 'pending':
                    markup.add(
                        types.InlineKeyboardButton("✅ Принять", callback_data=f"accept_app_{application_id}"),
                        types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_app_{application_id}")
                    )
                
                markup.add(
                    types.InlineKeyboardButton("⬅️ К откликам", callback_data="job_applications"),
                    types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                )
                
                self.bot.edit_message_text(
                    text=text,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    parse_mode='HTML',
                    reply_markup=markup
                )
                
        except Exception as e:
            self.logger.error(f"Ошибка в view_application_details: {e}")
    
    def accept_application(self, call, application_id):
        """Принимает отклик"""
        try:
            with self.app.app_context():
                application = Application.query.get(application_id)
                if not application:
                    self.bot.answer_callback_query(call.id, "Отклик не найден")
                    return
                
                application.status = 'accepted'
                db.session.commit()
                
                self.bot.answer_callback_query(call.id, "✅ Отклик принят!")
                self.view_application_details(call, application_id)
                
        except Exception as e:
            self.logger.error(f"Ошибка в accept_application: {e}")
    
    def reject_application(self, call, application_id):
        """Отклоняет отклик"""
        try:
            with self.app.app_context():
                application = Application.query.get(application_id)
                if not application:
                    self.bot.answer_callback_query(call.id, "Отклик не найден")
                    return
                
                application.status = 'rejected'
                db.session.commit()
                
                self.bot.answer_callback_query(call.id, "❌ Отклик отклонен")
                self.view_application_details(call, application_id)
                
        except Exception as e:
            self.logger.error(f"Ошибка в reject_application: {e}")
    
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        
        # === ОСНОВНЫЕ КОМАНДЫ ===
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            self.handle_start_command(message)
        
        @self.bot.message_handler(commands=['help'])
        def handle_help(message):
            self.handle_help_command(message)
        
        @self.bot.message_handler(commands=['menu'])
        def handle_menu(message):
            self.show_main_menu(message)
        
        # === КОМАНДЫ ДЛЯ РАБОТОДАТЕЛЕЙ ===
        @self.bot.message_handler(commands=['employer'])
        def handle_employer(message):
            self.switch_to_employer(message)
        
        @self.bot.message_handler(commands=['newjob'])
        def handle_new_job(message):
            self.start_job_creation(message)
        
        @self.bot.message_handler(commands=['myjobs'])
        def handle_my_jobs(message):
            self.show_employer_jobs(message)
        
        @self.bot.message_handler(commands=['applications'])
        def handle_applications(message):
            self.show_job_applications(message)
        
        # === КОМАНДЫ ДЛЯ СОИСКАТЕЛЕЙ ===
        @self.bot.message_handler(commands=['jobseeker'])
        def handle_jobseeker(message):
            self.switch_to_jobseeker(message)
        
        @self.bot.message_handler(commands=['jobs'])
        def handle_jobs(message):
            self.show_jobs_list(message)
        
        @self.bot.message_handler(commands=['search'])
        def handle_search(message):
            self.start_job_search(message)
        
        @self.bot.message_handler(commands=['myapps'])
        def handle_my_applications(message):
            self.show_my_applications(message)
        
        @self.bot.message_handler(commands=['subscribe'])
        def handle_subscribe(message):
            self.start_subscription_creation(message)
        
        @self.bot.message_handler(commands=['subscriptions'])
        def handle_subscriptions(message):
            self.show_subscriptions(message)
        
        # === КОМАНДЫ ПРОФИЛЯ ===
        @self.bot.message_handler(commands=['profile'])
        def handle_profile(message):
            self.show_profile(message)
        
        @self.bot.message_handler(commands=['settings'])
        def handle_settings(message):
            self.show_settings(message)
        
        # === БЫСТРЫЕ КОМАНДЫ ===
        @self.bot.message_handler(commands=['quick'])
        def handle_quick(message):
            self.show_quick_actions(message)
        
        @self.bot.message_handler(commands=['stats'])
        def handle_stats(message):
            self.show_user_stats(message)
        
        # === ОБРАБОТЧИКИ CALLBACK ===
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            self.handle_callback_query(call)
        
        # === ОБРАБОТЧИК ВСЕХ СООБЩЕНИЙ ===
        @self.bot.message_handler(func=lambda message: True)
        def handle_all_messages(message):
            self.handle_user_input(message)
    
    def handle_start_command(self, message):
        """Обработчик команды /start"""
        telegram_id = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
            user = self.get_user(telegram_id)
            
            welcome_text = f"""
🎉 <b>Добро пожаловать в HR Bot!</b>

Привет, {user.first_name}! 👋

Я помогу вам:
• 👔 <b>Работодателям</b> - найти лучших кандидатов
• 💼 <b>Соискателям</b> - найти работу мечты

<b>Выберите вашу роль:</b>
            """
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("👔 Я работодатель", callback_data="role_employer"),
                types.InlineKeyboardButton("💼 Я ищу работу", callback_data="role_jobseeker"),
                types.InlineKeyboardButton("ℹ️ Подробнее о боте", callback_data="about_bot")
            )
            
            self.bot.send_message(
                message.chat.id,
                welcome_text,
                parse_mode='HTML',
                reply_markup=markup
            )
    
    def handle_help_command(self, message):
        """Обработчик команды /help"""
        telegram_id = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
            user = self.get_user(telegram_id)
            
            if user and user.user_type == 'employer':
                help_text = """
📋 <b>Команды для работодателей:</b>

<b>Управление вакансиями:</b>
/newjob - Создать новую вакансию
/myjobs - Мои вакансии
/applications - Отклики на вакансии

<b>Быстрые действия:</b>
/quick - Быстрые действия
/stats - Моя статистика

<b>Общие команды:</b>
/profile - Мой профиль
/settings - Настройки
/menu - Главное меню
/help - Эта справка
                """
            else:
                help_text = """
📋 <b>Команды для соискателей:</b>

<b>Поиск работы:</b>
/jobs - Все вакансии
/search - Поиск вакансий
/myapps - Мои отклики

<b>Уведомления:</b>
/subscribe - Подписаться на уведомления
/subscriptions - Мои подписки

<b>Быстрые действия:</b>
/quick - Быстрые действия
/stats - Моя статистика

<b>Общие команды:</b>
/profile - Мой профиль
/settings - Настройки
/menu - Главное меню
/help - Эта справка
                """
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
            
            self.bot.send_message(
                message.chat.id,
                help_text,
                parse_mode='HTML',
                reply_markup=markup
            )
    
    def show_main_menu(self, message):
        """Показывает главное меню для команд"""
        telegram_id = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
            # Получаем пользователя заново из базы
            user = User.query.filter_by(telegram_id=telegram_id).first()
            
            print(f"DEBUG: Команда - Пользователь {telegram_id}, роль: {user.user_type}")
            
            # Переводим роль на русский
            role_names = {
                'employer': 'Работодатель',
                'jobseeker': 'Соискатель'
            }
            role_display = role_names.get(user.user_type, user.user_type.title())
            
            menu_text = f"🏠 <b>Главное меню</b>\n\nВы вошли как: {user.first_name}\nРоль: {role_display}"
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            if user.user_type == 'employer':
                markup.add(
                    types.InlineKeyboardButton("➕ Новая вакансия", callback_data="new_job"),
                    types.InlineKeyboardButton("📋 Мои вакансии", callback_data="my_jobs")
                )
                markup.add(
                    types.InlineKeyboardButton("📨 Отклики", callback_data="job_applications"),
                    types.InlineKeyboardButton("📊 Статистика", callback_data="employer_stats")
                )
            else:
                markup.add(
                    types.InlineKeyboardButton("🔍 Поиск работы", callback_data="search_jobs"),
                    types.InlineKeyboardButton("📋 Все вакансии", callback_data="all_jobs")
                )
                markup.add(
                    types.InlineKeyboardButton("📨 Мои отклики", callback_data="my_applications"),
                    types.InlineKeyboardButton("🔔 Подписки", callback_data="subscriptions")
                )
            
            markup.add(
                types.InlineKeyboardButton("👤 Профиль", callback_data="profile"),
                types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
            )
            markup.add(
                types.InlineKeyboardButton("🔄 Сменить роль", callback_data="switch_role"),
                types.InlineKeyboardButton("❓ Помощь", callback_data="help")
            )
            
            self.bot.send_message(
                message.chat.id,
                menu_text,
                parse_mode='HTML',
                reply_markup=markup
            )

    def show_main_menu_callback(self, call):
        """Показывает главное меню из callback"""
        telegram_id = call.from_user.id
        
        with self.app.app_context():
            user = User.query.filter_by(telegram_id=telegram_id).first()
            
            print(f"DEBUG: Callback - Пользователь {telegram_id}, роль: {user.user_type}")
            
            # Переводим роль на русский
            role_names = {
                'employer': 'Работодатель',
                'jobseeker': 'Соискатель'
            }
            role_display = role_names.get(user.user_type, user.user_type.title())
            
            menu_text = f"🏠 <b>Главное меню</b>\n\nВы вошли как: {user.first_name}\nРоль: {role_display}"
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            if user.user_type == 'employer':
                markup.add(
                    types.InlineKeyboardButton("➕ Новая вакансия", callback_data="new_job"),
                    types.InlineKeyboardButton("📋 Мои вакансии", callback_data="my_jobs")
                )
                markup.add(
                    types.InlineKeyboardButton("📨 Отклики", callback_data="job_applications"),
                    types.InlineKeyboardButton("📊 Статистика", callback_data="employer_stats")
                )
            else:
                markup.add(
                    types.InlineKeyboardButton("🔍 Поиск работы", callback_data="search_jobs"),
                    types.InlineKeyboardButton("📋 Все вакансии", callback_data="all_jobs")
                )
                markup.add(
                    types.InlineKeyboardButton("📨 Мои отклики", callback_data="my_applications"),
                    types.InlineKeyboardButton("🔔 Подписки", callback_data="subscriptions")
                )
            
            markup.add(
                types.InlineKeyboardButton("👤 Профиль", callback_data="profile"),
                types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
            )
            markup.add(
                types.InlineKeyboardButton("🔄 Сменить роль", callback_data="switch_role"),
                types.InlineKeyboardButton("❓ Помощь", callback_data="help")
            )
            
            self.bot.edit_message_text(
                text=menu_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
    
    def show_quick_actions(self, message):
        """Показывает быстрые действия"""
        telegram_id = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
            user = self.get_user(telegram_id)
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            if user.user_type == 'employer':
                markup.add(
                    types.InlineKeyboardButton("⚡ Быстрая вакансия", callback_data="new_job"),
                    types.InlineKeyboardButton("👀 Мои вакансии", callback_data="my_jobs")
                )
                markup.add(
                    types.InlineKeyboardButton("📨 Новые отклики", callback_data="job_applications"),
                    types.InlineKeyboardButton("📊 Статистика", callback_data="employer_stats")
                )
            else:
                markup.add(
                    types.InlineKeyboardButton("🆕 Новые вакансии", callback_data="all_jobs"),
                    types.InlineKeyboardButton("🎯 Все вакансии", callback_data="all_jobs")
                )
                markup.add(
                    types.InlineKeyboardButton("📨 Мои отклики", callback_data="my_applications"),
                    types.InlineKeyboardButton("🔔 Подписки", callback_data="subscriptions")
                )
            
            markup.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
            
            self.bot.send_message(
                message.chat.id,
                "⚡ <b>Быстрые действия</b>\n\nВыберите действие:",
                parse_mode='HTML',
                reply_markup=markup
            )
    
    def start_job_creation(self, message):
        """Начинает процесс создания вакансии"""
        telegram_id = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
            user = self.get_user(telegram_id)
            
            if not user or user.user_type != 'employer':
                self.bot.send_message(
                    message.chat.id,
                    "❌ Только работодатели могут создавать вакансии.\n\nИспользуйте /employer для смены роли."
                )
                return
            
            # Устанавливаем состояние пользователя
            self.user_states[message.from_user.id] = {
                'action': 'creating_job',
                'step': 'title',
                'job_data': {}
            }
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_job_creation"))
            
            self.bot.send_message(
                message.chat.id,
                "📝 <b>Создание новой вакансии</b>\n\n"
                "Шаг 1/5: Введите название вакансии\n"
                "Например: <i>Python разработчик</i>, <i>Менеджер по продажам</i>",
                parse_mode='HTML',
                reply_markup=markup
            )
    
    def show_jobs_list(self, message, page=1):
        """Показывает список вакансий"""
        with self.app.app_context():
            # Простой запрос всех активных вакансий
            jobs = Job.query.filter_by(is_active=True).offset((page-1)*self.JOBS_PER_PAGE).limit(self.JOBS_PER_PAGE).all()
            total_jobs = Job.query.filter_by(is_active=True).count()
            total_pages = (total_jobs + self.JOBS_PER_PAGE - 1) // self.JOBS_PER_PAGE
            
            if not jobs:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
                
                self.bot.send_message(
                    message.chat.id,
                    "😔 Вакансий пока нет.\n\nПопробуйте позже или создайте первую вакансию!",
                    reply_markup=markup
                )
                return
            
            text = f"📋 <b>Все вакансии</b> (страница {page}/{total_pages})\n\n"
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            
            for job in jobs:
                job_text = f"💼 <b>{job.title}</b>\n"
                job_text += f"🏢 {job.company}\n"
                job_text += f"📍 {job.location or 'Не указано'}\n"
                
                if job.salary_min and job.salary_max:
                    job_text += f"💰 {job.salary_min:,} - {job.salary_max:,} руб.\n"
                elif job.salary_min:
                    job_text += f"💰 от {job.salary_min:,} руб.\n"
                elif job.salary_max:
                    job_text += f"💰 до {job.salary_max:,} руб.\n"
                else:
                    job_text += f"💰 По договоренности\n"
                
                text += job_text + "\n"
                
                markup.add(
                    types.InlineKeyboardButton(
                        f"👀 {job.title[:30]}...",
                        callback_data=f"view_job_{job.id}"
                    )
                )
            
            # Навигация
            nav_buttons = []
            if page > 1:
                nav_buttons.append(
                    types.InlineKeyboardButton("⬅️ Назад", callback_data=f"jobs_page_{page-1}")
                )
            if page < total_pages:
                nav_buttons.append(
                    types.InlineKeyboardButton("➡️ Далее", callback_data=f"jobs_page_{page+1}")
                )
            
            if nav_buttons:
                markup.row(*nav_buttons)
            
            markup.add(
                types.InlineKeyboardButton("🔍 Поиск", callback_data="search_jobs"),
                types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            )
            
            self.bot.send_message(
                message.chat.id,
                text,
                parse_mode='HTML',
                reply_markup=markup
            )

    def show_employer_jobs(self, message):
        """Показывает вакансии работодателя"""
        telegram_id = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
            user = self.get_user(telegram_id)
            
            if user.user_type != 'employer':
                self.bot.send_message(message.chat.id, "❌ Только работодатели могут просматривать свои вакансии")
                return
            
            jobs = Job.query.filter_by(employer_id=user.id, is_active=True).all()
            
            if not jobs:
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("➕ Создать первую вакансию", callback_data="new_job"),
                    types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                )
                
                self.bot.send_message(
                    message.chat.id,
                    "📋 <b>Мои вакансии</b>\n\n😔 У вас пока нет активных вакансий.\n\nСоздайте первую вакансию!",
                    parse_mode='HTML',
                    reply_markup=markup
                )
                return
            
            text = f"📋 <b>Мои вакансии</b> ({len(jobs)})\n\n"
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            
            for job in jobs:
                # Считаем отклики
                applications_count = Application.query.filter_by(job_id=job.id).count()
                
                job_text = f"💼 <b>{job.title}</b>\n"
                job_text += f"🏢 {job.company}\n"
                job_text += f"📨 Откликов: {applications_count}\n"
                job_text += f"📅 {job.created_at.strftime('%d.%m.%Y')}\n\n"
                
                text += job_text
                
                markup.add(
                    types.InlineKeyboardButton(
                        f"👀 {job.title[:25]}... ({applications_count} откликов)",
                        callback_data=f"employer_job_{job.id}"
                    )
                )
            
            markup.add(
                types.InlineKeyboardButton("➕ Новая вакансия", callback_data="new_job"),
                types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            )
            
            self.bot.send_message(
                message.chat.id,
                text,
                parse_mode='HTML',
                reply_markup=markup
            )

    def show_job_applications(self, message):
        """Показывает отклики на вакансии работодателя"""
        telegram_id = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
            user = self.get_user(telegram_id)
            
            if user.user_type != 'employer':
                self.bot.send_message(message.chat.id, "❌ Только работодатели могут просматривать отклики")
                return
            
            # Получаем все вакансии работодателя
            jobs = Job.query.filter_by(employer_id=user.id, is_active=True).all()
            
            if not jobs:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
                
                self.bot.send_message(
                    message.chat.id,
                    "📨 <b>Отклики на вакансии</b>\n\n😔 У вас нет активных вакансий.",
                    parse_mode='HTML',
                    reply_markup=markup
                )
                return
            
            # Собираем все отклики на все вакансии
            all_applications = []
            for job in jobs:
                applications = Application.query.filter_by(job_id=job.id).all()
                for app in applications:
                    app.job = job  # Добавляем информацию о вакансии
                    all_applications.append(app)
            
            if not all_applications:
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("📋 Мои вакансии", callback_data="my_jobs"),
                    types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                )
                
                self.bot.send_message(
                    message.chat.id,
                    "📨 <b>Отклики на вакансии</b>\n\n😔 Пока нет откликов на ваши вакансии.",
                    parse_mode='HTML',
                    reply_markup=markup
                )
                return
            
            # Сортируем по дате (новые сначала)
            all_applications.sort(key=lambda x: x.created_at, reverse=True)
            
            text = f"📨 <b>Отклики на вакансии</b> ({len(all_applications)})\n\n"
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            
            for app in all_applications:
                # Получаем информацию о соискателе
                applicant = User.query.get(app.applicant_id)
                
                status_emoji = {
                    'pending': '⏳',
                    'accepted': '✅',
                    'rejected': '❌'
                }.get(app.status, '❓')
                
                app_text = f"{status_emoji} <b>{app.job.title}</b>\n"
                app_text += f"👤 {applicant.get_full_name() if applicant else 'Неизвестный'}\n"
                app_text += f"📅 {app.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                
                text += app_text
                
                markup.add(
                    types.InlineKeyboardButton(
                        f"{status_emoji} {applicant.get_full_name()[:20]}... → {app.job.title[:15]}...",
                        callback_data=f"view_application_{app.id}"
                    )
                )
            
            markup.add(
                types.InlineKeyboardButton("📋 Мои вакансии", callback_data="my_jobs"),
                types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            )
            
            self.bot.send_message(
                message.chat.id,
                text,
                parse_mode='HTML',
                reply_markup=markup
            )

    def show_my_applications(self, message):
        """Показывает отклики пользователя"""
        telegram_id = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
            user = self.get_user(telegram_id)
            
            if user.user_type != 'jobseeker':
                self.bot.send_message(message.chat.id, "❌ Только соискатели могут просматривать свои отклики")
                return
            
            applications = Application.query.filter_by(applicant_id=user.id).all()
            
            if not applications:
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("📋 Посмотреть вакансии", callback_data="all_jobs"),
                    types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                )
                
                self.bot.send_message(
                    message.chat.id,
                    "📨 <b>Мои отклики</b>\n\n😔 У вас пока нет откликов.\n\nПосмотрите доступные вакансии!",
                    parse_mode='HTML',
                    reply_markup=markup
                )
                return
            
            text = f"📨 <b>Мои отклики</b> ({len(applications)})\n\n"
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            
            for app in applications:
                job = Job.query.get(app.job_id)
                if job:
                    status_emoji = {
                        'pending': '⏳',
                        'accepted': '✅',
                        'rejected': '❌'
                    }.get(app.status, '❓')
                    
                    app_text = f"{status_emoji} <b>{job.title}</b>\n"
                    app_text += f"🏢 {job.company}\n"
                    app_text += f"📅 {app.created_at.strftime('%d.%m.%Y')}\n\n"
                    
                    text += app_text
                    
                    markup.add(
                        types.InlineKeyboardButton(
                            f"{status_emoji} {job.title[:25]}...",
                            callback_data=f"view_job_{job.id}"
                        )
                    )
            
            markup.add(
                types.InlineKeyboardButton("📋 Все вакансии", callback_data="all_jobs"),
                types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            )
            
            self.bot.send_message(
                message.chat.id,
                text,
                parse_mode='HTML',
                reply_markup=markup
            )

    def show_employer_stats(self, message):
        """Показывает статистику работодателя"""
        telegram_id = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
            user = self.get_user(telegram_id)
            
            if user.user_type != 'employer':
                self.bot.send_message(message.chat.id, "❌ Только работодатели могут просматривать статистику")
                return
            
            # Получаем статистику
            total_jobs = Job.query.filter_by(employer_id=user.id, is_active=True).count()
            total_applications = db.session.query(Application).join(Job).filter(Job.employer_id == user.id).count()
            pending_applications = db.session.query(Application).join(Job).filter(
                Job.employer_id == user.id, 
                Application.status == 'pending'
            ).count()
            accepted_applications = db.session.query(Application).join(Job).filter(
                Job.employer_id == user.id, 
                Application.status == 'accepted'
            ).count()
            
            text = f"📊 <b>Статистика работодателя</b>\n\n"
            text += f"📋 <b>Активных вакансий:</b> {total_jobs}\n"
            text += f"📨 <b>Всего откликов:</b> {total_applications}\n"
            text += f"⏳ <b>Ожидают рассмотрения:</b> {pending_applications}\n"
            text += f"✅ <b>Принято:</b> {accepted_applications}\n\n"
            
            if total_jobs > 0:
                avg_applications = total_applications / total_jobs
                text += f"📈 <b>Среднее откликов на вакансию:</b> {avg_applications:.1f}\n"
            
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("📋 Мои вакансии", callback_data="my_jobs"),
                types.InlineKeyboardButton("📨 Отклики", callback_data="job_applications")
            )
            markup.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
            
            self.bot.send_message(
                message.chat.id,
                text,
                parse_mode='HTML',
                reply_markup=markup
            )
    
    def handle_callback_query(self, call):
        """Обработчик callback запросов"""
        try:
            data = call.data
            telegram_id = self.get_or_create_user(call.from_user)
            
            # Основные действия
            if data == "main_menu":
                self.show_main_menu_callback(call)
            elif data == "help":
                fake_message = type('obj', (object,), {
                    'chat': call.message.chat,
                    'from_user': call.from_user
                })
                self.handle_help_command(fake_message)
            elif data.startswith("role_"):
                self.handle_role_selection(call)
            elif data == "switch_role":
                self.show_role_switch(call)
            elif data == "new_job":
                fake_message = type('obj', (object,), {
                    'chat': call.message.chat,
                    'from_user': call.from_user
                })
                self.start_job_creation(fake_message)
            elif data == "my_jobs":
                fake_message = type('obj', (object,), {
                    'chat': call.message.chat,
                    'from_user': call.from_user
                })
                self.show_employer_jobs(fake_message)
            elif data == "job_applications":
                fake_message = type('obj', (object,), {
                    'chat': call.message.chat,
                    'from_user': call.from_user
                })
                self.show_job_applications(fake_message)
            elif data == "employer_stats":
                fake_message = type('obj', (object,), {
                    'chat': call.message.chat,
                    'from_user': call.from_user
                })
                self.show_employer_stats(fake_message)
            elif data == "all_jobs":
                fake_message = type('obj', (object,), {
                    'chat': call.message.chat,
                    'from_user': call.from_user
                })
                self.show_jobs_list(fake_message)
            elif data == "my_applications":
                fake_message = type('obj', (object,), {
                    'chat': call.message.chat,
                    'from_user': call.from_user
                })
                self.show_my_applications(fake_message)
            elif data.startswith("view_job_"):
                job_id = int(data.split("_")[2])
                self.show_job_details(call, job_id)
            elif data.startswith("view_application_"):
                application_id = int(data.split("_")[2])
                self.view_application_details(call, application_id)
            elif data.startswith("accept_app_"):
                application_id = int(data.split("_")[2])
                self.accept_application(call, application_id)
            elif data.startswith("reject_app_"):
                application_id = int(data.split("_")[2])
                self.reject_application(call, application_id)
            elif data.startswith("apply_job_"):
                job_id = int(data.split("_")[2])
                self.start_job_application(call, job_id)
            elif data.startswith("jobs_page_"):
                page = int(data.split("_")[2])
                fake_message = type('obj', (object,), {
                    'chat': call.message.chat,
                    'from_user': call.from_user
                })
                self.show_jobs_list(fake_message, page)
            elif data == "already_applied":
                self.bot.answer_callback_query(call.id, "Вы уже откликнулись на эту вакансию")
            elif data == "about_bot":
                self.show_about_bot(call)
            elif data == "cancel_job_creation":
                # Сбрасываем состояние пользователя
                if call.from_user.id in self.user_states:
                    del self.user_states[call.from_user.id]
                self.bot.edit_message_text(
                    text="❌ Создание вакансии отменено",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
                self.show_main_menu_callback(call)
            elif data == "confirm_job_creation":
                self.confirm_job_creation(call)
            else:
                self.bot.answer_callback_query(call.id, "🔧 Функция в разработке")
            
            self.bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Ошибка в handle_callback_query: {e}")
            self.bot.answer_callback_query(call.id, "Произошла ошибка")

    def confirm_job_creation(self, call):
        """Подтверждает создание вакансии"""
        try:
            user_id = call.from_user.id
            if user_id not in self.user_states:
                self.bot.answer_callback_query(call.id, "Сессия истекла, начните заново")
                return
            
            state = self.user_states[user_id]
            job_data = state.get('job_data', {})
            
            with self.app.app_context():
                user = self.get_user(call.from_user.id)
                
                # Создаем вакансию
                job = Job(
                    title=job_data.get('title', ''),
                    company=job_data.get('company', ''),
                    location=job_data.get('location', ''),
                    salary_min=job_data.get('salary_min'),
                    salary_max=job_data.get('salary_max'),
                    description=job_data.get('description', ''),
                    employer_id=user.id,
                    employment_type='full-time',
                    experience_level='middle',
                    skills_required='',
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(job)
                db.session.commit()
                
                # Сбрасываем состояние
                del self.user_states[user_id]
                
                text = f"✅ <b>Вакансия создана успешно!</b>\n\n"
                text += f"💼 <b>{job.title}</b>\n"
                text += f"🏢 {job.company}\n"
                text += f"📍 {job.location}\n\n"
                text += f"Вакансия опубликована и доступна для соискателей!"
                
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("📋 Мои вакансии", callback_data="my_jobs"),
                    types.InlineKeyboardButton("➕ Еще вакансия", callback_data="new_job")
                )
                markup.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
                
                self.bot.edit_message_text(
                    text=text,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    parse_mode='HTML',
                    reply_markup=markup
                )
                
        except Exception as e:
            self.logger.error(f"Ошибка в confirm_job_creation: {e}")
    
    def show_about_bot(self, call):
        """Показывает информацию о боте"""
        text = """
ℹ️ <b>О HR Bot</b>

Этот бот поможет вам в поиске работы и подборе персонала.

<b>Для соискателей:</b>
• Поиск актуальных вакансий
• Быстрые отклики на интересные предложения
• Уведомления о новых вакансиях
• Персональные рекомендации

<b>Для работодателей:</b>
• Размещение вакансий
• Управление откликами
• Статистика по вакансиям
• Поиск кандидатов

Выберите свою роль и начните использовать бота!
        """
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("👔 Я работодатель", callback_data="role_employer"),
            types.InlineKeyboardButton("💼 Я ищу работу", callback_data="role_jobseeker"),
            types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        )
        
        self.bot.edit_message_text(
            text=text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )
    
    def handle_user_input(self, message):
        """Обработчик пользовательского ввода"""
        user_id = message.from_user.id
        
        if user_id not in self.user_states:
            # Если нет активного состояния, показываем меню
            self.show_main_menu(message)
            return
        
        state = self.user_states[user_id]
        action = state.get('action')
        
        if action == 'creating_job':
            self.handle_job_creation_input(message, state)
        elif action == 'searching_jobs':
            self.handle_job_search_input(message, state)
        elif action == 'creating_subscription':
            self.handle_subscription_input(message, state)
        else:
            # Неизвестное состояние, сбрасываем
            del self.user_states[user_id]
            self.show_main_menu(message)
    
    def handle_job_creation_input(self, message, state):
        """Обработчик ввода при создании вакансии"""
        step = state['step']
        job_data = state['job_data']
        
        if step == 'title':
            job_data['title'] = message.text
            state['step'] = 'company'
            self.bot.send_message(
                message.chat.id,
                "Шаг 2/5: Введите название компании"
            )
        elif step == 'company':
            job_data['company'] = message.text
            state['step'] = 'location'
            self.bot.send_message(
                message.chat.id,
                "Шаг 3/5: Введите местоположение\n"
                "Например: <i>Москва</i>, <i>Санкт-Петербург</i>, <i>Удаленно</i>",
                parse_mode='HTML'
            )
        elif step == 'location':
            job_data['location'] = message.text
            state['step'] = 'salary'
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⏭️ Пропустить", callback_data="skip_salary"))
            
            self.bot.send_message(
                message.chat.id,
                "Шаг 4/5: Введите зарплату\n"
                "Формат: <i>от 100000</i>, <i>100000-150000</i> или <i>до 200000</i>\n"
                "Или нажмите 'Пропустить'",
                parse_mode='HTML',
                reply_markup=markup
            )
        elif step == 'salary':
            self.parse_salary(message.text, job_data)
            state['step'] = 'description'
            self.bot.send_message(
                message.chat.id,
                "Шаг 5/5: Введите описание вакансии\n"
                "Опишите обязанности, требования и условия работы"
            )
        elif step == 'description':
            job_data['description'] = message.text
            state['step'] = 'confirm'
            self.show_job_confirmation(message, job_data)
    
    def parse_salary(self, salary_text: str, job_data: dict):
        """Парсит зарплату из текста"""
        import re
        
        # Удаляем все кроме цифр, тире и слов "от", "до"
        clean_text = re.sub(r'[^\d\-от до]', ' ', salary_text.lower())
        
        # Ищем числа
        numbers = re.findall(r'\d+', clean_text)
        
        if not numbers:
            return
        
        if 'от' in clean_text and 'до' in clean_text:
            # Диапазон: от X до Y
            if len(numbers) >= 2:
                job_data['salary_min'] = int(numbers[0])
                job_data['salary_max'] = int(numbers[1])
        elif 'от' in clean_text:
            # От X
            job_data['salary_min'] = int(numbers[0])
        elif 'до' in clean_text:
            # До X
            job_data['salary_max'] = int(numbers[0])
        elif '-' in salary_text and len(numbers) >= 2:
            # X-Y
            job_data['salary_min'] = int(numbers[0])
            job_data['salary_max'] = int(numbers[1])
        else:
            # Одно число - считаем минимальной зарплатой
            job_data['salary_min'] = int(numbers[0])
    
    def show_job_confirmation(self, message, job_data):
        """Показывает подтверждение создания вакансии"""
        text = "📋 <b>Подтверждение создания вакансии</b>\n\n"
        text += f"💼 <b>Название:</b> {job_data['title']}\n"
        text += f"🏢 <b>Компания:</b> {job_data['company']}\n"
        text += f"📍 <b>Местоположение:</b> {job_data['location']}\n"
        
        if 'salary_min' in job_data or 'salary_max' in job_data:
            salary_min = job_data.get('salary_min', 0)
            salary_max = job_data.get('salary_max', 0)
            if salary_min and salary_max:
                text += f"💰 <b>Зарплата:</b> {salary_min:,} - {salary_max:,} руб.\n"
            elif salary_min:
                text += f"💰 <b>Зарплата:</b> от {salary_min:,} руб.\n"
            elif salary_max:
                text += f"💰 <b>Зарплата:</b> до {salary_max:,} руб.\n"
        else:
            text += f"💰 <b>Зарплата:</b> По договоренности\n"
        
        text += f"\n📝 <b>Описание:</b>\n{job_data['description'][:200]}..."
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✅ Создать", callback_data="confirm_job_creation"),
            types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_job_creation")
        )
        
        self.bot.send_message(
            message.chat.id,
            text,
            parse_mode='HTML',
            reply_markup=markup
        )
    
    def switch_to_employer(self, message):
        """Переключает пользователя в режим работодателя"""
        telegram_id = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
            user = User.query.filter_by(telegram_id=telegram_id).first()
            user.user_type = 'employer'
            db.session.commit()
        
        self.bot.send_message(
            message.chat.id,
            "👔 Вы переключились в режим работодателя!\n\n"
            "Теперь вы можете:\n"
            "• Создавать вакансии\n"
            "• Просматривать отклики\n"
            "• Управлять своими вакансиями\n\n"
            "Используйте /menu для доступа к функциям."
        )
    
    def switch_to_jobseeker(self, message):
        """Переключает пользователя в режим соискателя"""
        telegram_id = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
            user = User.query.filter_by(telegram_id=telegram_id).first()
            user.user_type = 'jobseeker'
            db.session.commit()
        
        self.bot.send_message(
            message.chat.id,
            "💼 Вы переключились в режим соискателя!\n\n"
            "Теперь вы можете:\n"
            "• Искать вакансии\n"
            "• Откликаться на вакансии\n"
            "• Подписываться на уведомления\n\n"
            "Используйте /menu для доступа к функциям."
        )
    
    # Заглушки для оставшихся методов
    def start_job_search(self, message):
        self.bot.send_message(message.chat.id, "🔧 Функция в разработке")
    
    def start_subscription_creation(self, message):
        self.bot.send_message(message.chat.id, "🔧 Функция в разработке")
    
    def show_subscriptions(self, message):
        self.bot.send_message(message.chat.id, "🔧 Функция в разработке")
    
    def show_profile(self, message):
        self.bot.send_message(message.chat.id, "🔧 Функция в разработке")
    
    def show_settings(self, message):
        self.bot.send_message(message.chat.id, "🔧 Функция в разработке")
    
    def show_user_stats(self, message):
        self.bot.send_message(message.chat.id, "🔧 Функция в разработке")
    
    def handle_job_search_input(self, message, state):
        self.bot.send_message(message.chat.id, "🔧 Функция в разработке")
    
    def handle_subscription_input(self, message, state):
        self.bot.send_message(message.chat.id, "🔧 Функция в разработке")
    
    def start_polling(self):
        """Запускает бота в режиме polling"""
        logger.info("Запуск Telegram-бота в режиме polling...")
        self.bot.polling(none_stop=True)
    
    def handle_webhook(self):
        """Обработчик webhook"""
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            self.bot.process_new_updates([update])
            return "OK"
        else:
            return "Bad Request", 400

