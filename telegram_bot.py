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

from src.models.user import User, db
from src.models.job import Job
from src.models.application import Application
from src.models.subscription import Subscription

logger = logging.getLogger(__name__)

class TelegramHRBot:
    """Основной класс Telegram HR Bot с оптимизированными командами"""
    
    def __init__(self, token: str, flask_app: Flask):
        self.bot = telebot.TeleBot(token)
        self.app = flask_app
        self.user_states = {}  # Хранение состояний пользователей
        self.setup_handlers()
        
        # Константы для пагинации
        self.JOBS_PER_PAGE = 5
        self.APPLICATIONS_PER_PAGE = 5
        
        logger.info("TelegramHRBot инициализирован")
    
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
    
    def get_or_create_user(self, telegram_user) -> User:
        """Получает или создает пользователя"""
        with self.app.app_context():
            user = User.find_by_telegram_id(telegram_user.id)
            if not user:
                user = User.create_from_telegram(telegram_user)
                logger.info(f"Создан новый пользователь: {user.telegram_id}")
            else:
                user.update_last_activity()
            return user
    
    def handle_start_command(self, message):
        """Обработчик команды /start"""
        user = self.get_or_create_user(message.from_user)
        
        welcome_text = f"""
🎉 <b>Добро пожаловать в HR Bot!</b>

Привет, {user.get_full_name()}! 👋

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
        user = self.get_or_create_user(message.from_user)
        
        if user.is_employer():
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
        """Показывает главное меню"""
        user = self.get_or_create_user(message.from_user)
        
        menu_text = f"🏠 <b>Главное меню</b>\n\nВы вошли как: {user.get_full_name()}\nРоль: {user.user_type.title()}"
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        if user.is_employer():
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
    
    def show_quick_actions(self, message):
        """Показывает быстрые действия"""
        user = self.get_or_create_user(message.from_user)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        if user.is_employer():
            markup.add(
                types.InlineKeyboardButton("⚡ Быстрая вакансия", callback_data="quick_job"),
                types.InlineKeyboardButton("👀 Новые отклики", callback_data="new_applications")
            )
            markup.add(
                types.InlineKeyboardButton("📈 Сегодняшняя статистика", callback_data="today_stats"),
                types.InlineKeyboardButton("🔥 Популярные вакансии", callback_data="popular_jobs")
            )
        else:
            markup.add(
                types.InlineKeyboardButton("🆕 Новые вакансии", callback_data="latest_jobs"),
                types.InlineKeyboardButton("🎯 Рекомендации", callback_data="recommended_jobs")
            )
            markup.add(
                types.InlineKeyboardButton("💰 Высокооплачиваемые", callback_data="high_salary_jobs"),
                types.InlineKeyboardButton("🏠 Удаленная работа", callback_data="remote_jobs")
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
        user = self.get_or_create_user(message.from_user)
        
        if not user.is_employer():
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
            "Шаг 1/6: Введите название вакансии\n"
            "Например: <i>Python разработчик</i>, <i>Менеджер по продажам</i>",
            parse_mode='HTML',
            reply_markup=markup
        )
    
    def show_jobs_list(self, message, page=1):
        """Показывает список вакансий"""
        with self.app.app_context():
            pagination = Job.search(page=page, per_page=self.JOBS_PER_PAGE)
            jobs = pagination.items
            
            if not jobs:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
                
                self.bot.send_message(
                    message.chat.id,
                    "😔 Вакансий пока нет.\n\nПопробуйте позже или создайте первую вакансию!",
                    reply_markup=markup
                )
                return
            
            text = f"📋 <b>Вакансии</b> (страница {page}/{pagination.pages})\n\n"
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            
            for job in jobs:
                job_text = f"💼 <b>{job.title}</b>\n"
                job_text += f"🏢 {job.company}\n"
                job_text += f"📍 {job.location or 'Не указано'}\n"
                job_text += f"💰 {job.get_salary_range()}\n"
                
                text += job_text + "\n"
                
                markup.add(
                    types.InlineKeyboardButton(
                        f"👀 {job.title[:30]}...",
                        callback_data=f"view_job_{job.id}"
                    )
                )
            
            # Навигация
            nav_buttons = []
            if pagination.has_prev:
                nav_buttons.append(
                    types.InlineKeyboardButton("⬅️ Назад", callback_data=f"jobs_page_{page-1}")
                )
            if pagination.has_next:
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
    
    def handle_callback_query(self, call):
        """Обработчик callback запросов"""
        try:
            data = call.data
            user = self.get_or_create_user(call.from_user)
            
            # Основные действия
            if data == "main_menu":
                self.show_main_menu(call.message)
            elif data == "help":
                self.handle_help_command(call.message)
            elif data.startswith("role_"):
                self.handle_role_selection(call, data.split("_")[1])
            elif data == "switch_role":
                self.show_role_switch(call)
            elif data.startswith("view_job_"):
                job_id = int(data.split("_")[2])
                self.show_job_details(call, job_id)
            elif data.startswith("apply_job_"):
                job_id = int(data.split("_")[2])
                self.start_job_application(call, job_id)
            elif data.startswith("jobs_page_"):
                page = int(data.split("_")[2])
                self.show_jobs_list(call.message, page)
            # Добавить остальные обработчики...
            
            self.bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Ошибка в handle_callback_query: {e}")
            self.bot.answer_callback_query(call.id, "Произошла ошибка")
    
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
                "Шаг 2/6: Введите название компании"
            )
        elif step == 'company':
            job_data['company'] = message.text
            state['step'] = 'location'
            self.bot.send_message(
                message.chat.id,
                "Шаг 3/6: Введите местоположение\n"
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
                "Шаг 4/6: Введите зарплату\n"
                "Формат: <i>от 100000</i>, <i>100000-150000</i> или <i>до 200000</i>",
                parse_mode='HTML',
                reply_markup=markup
            )
        elif step == 'salary':
            self.parse_salary(message.text, job_data)
            state['step'] = 'description'
            self.bot.send_message(
                message.chat.id,
                "Шаг 5/6: Введите описание вакансии\n"
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
        
        text += f"\n📝 <b>Описание:</b>\n{job_data['description'][:200]}..."
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✅ Создать", callback_data="confirm_job_creation"),
            types.InlineKeyboardButton("✏️ Редактировать", callback_data="edit_job")
        )
        markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_job_creation"))
        
        self.bot.send_message(
            message.chat.id,
            text,
            parse_mode='HTML',
            reply_markup=markup
        )
    
    def switch_to_employer(self, message):
        """Переключает пользователя в режим работодателя"""
        user = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
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
        user = self.get_or_create_user(message.from_user)
        
        with self.app.app_context():
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

