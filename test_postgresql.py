#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности Telegram HR Bot с PostgreSQL
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Добавляем путь к исходному коду
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Настройка тестового окружения
os.environ['FLASK_ENV'] = 'testing'
os.environ['POSTGRES_DB'] = 'telegram_hr_bot_test'
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'

from src.main import app, db
from src.models.user import User
from src.models.job import Job
from src.models.application import Application
from src.models.subscription import Subscription

class TestDatabaseModels(unittest.TestCase):
    """Тестирование моделей базы данных"""
    
    def setUp(self):
        """Настройка тестового окружения"""
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Создание тестовых таблиц
        db.create_all()
        
    def tearDown(self):
        """Очистка после тестов"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        user = User(
            telegram_id=123456789,
            username='test_user',
            first_name='Тест',
            last_name='Пользователь',
            role='candidate'
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Проверка сохранения
        saved_user = User.query.filter_by(telegram_id=123456789).first()
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.username, 'test_user')
        self.assertEqual(saved_user.role, 'candidate')
        self.assertTrue(saved_user.is_active)
    
    def test_job_creation(self):
        """Тест создания вакансии"""
        # Создание работодателя
        employer = User(
            telegram_id=987654321,
            username='employer',
            first_name='Работодатель',
            role='employer'
        )
        db.session.add(employer)
        db.session.commit()
        
        # Создание вакансии
        job = Job(
            title='Python Developer',
            description='Требуется опытный Python разработчик',
            company='ТестКомпания',
            location='Москва',
            salary_min=100000,
            salary_max=150000,
            employment_type='full_time',
            experience_level='middle',
            skills='Python, Flask, PostgreSQL',
            employer_id=987654321
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Проверка сохранения
        saved_job = Job.query.filter_by(title='Python Developer').first()
        self.assertIsNotNone(saved_job)
        self.assertEqual(saved_job.company, 'ТестКомпания')
        self.assertEqual(saved_job.employer_id, 987654321)
        self.assertTrue(saved_job.is_active)
    
    def test_application_creation(self):
        """Тест создания отклика на вакансию"""
        # Создание пользователей
        employer = User(telegram_id=111, username='emp', first_name='Emp', role='employer')
        candidate = User(telegram_id=222, username='cand', first_name='Cand', role='candidate')
        
        db.session.add_all([employer, candidate])
        db.session.commit()
        
        # Создание вакансии
        job = Job(
            title='Test Job',
            description='Test Description',
            company='Test Company',
            location='Test Location',
            employer_id=111
        )
        db.session.add(job)
        db.session.commit()
        
        # Создание отклика
        application = Application(
            job_id=job.id,
            candidate_id=222,
            cover_letter='Тестовое сопроводительное письмо',
            contact_info='test@example.com'
        )
        
        db.session.add(application)
        db.session.commit()
        
        # Проверка сохранения
        saved_application = Application.query.filter_by(job_id=job.id).first()
        self.assertIsNotNone(saved_application)
        self.assertEqual(saved_application.candidate_id, 222)
        self.assertEqual(saved_application.status, 'new')
    
    def test_subscription_creation(self):
        """Тест создания подписки на уведомления"""
        # Создание пользователя
        user = User(telegram_id=333, username='subscriber', first_name='Sub', role='candidate')
        db.session.add(user)
        db.session.commit()
        
        # Создание подписки
        subscription = Subscription(
            user_id=333,
            keywords='Python, Django',
            location='Москва',
            salary_min=80000,
            frequency='daily'
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        # Проверка сохранения
        saved_subscription = Subscription.query.filter_by(user_id=333).first()
        self.assertIsNotNone(saved_subscription)
        self.assertEqual(saved_subscription.keywords, 'Python, Django')
        self.assertTrue(saved_subscription.is_active)

class TestBotFunctionality(unittest.TestCase):
    """Тестирование функциональности бота"""
    
    def setUp(self):
        """Настройка тестового окружения"""
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Мок объекты для Telegram
        self.mock_bot = Mock()
        self.mock_message = Mock()
        self.mock_message.from_user.id = 123456789
        self.mock_message.from_user.username = 'test_user'
        self.mock_message.from_user.first_name = 'Тест'
        self.mock_message.chat.id = 123456789
        
    def tearDown(self):
        """Очистка после тестов"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    @patch('src.bot.telegram_bot.TelegramHRBot')
    def test_user_registration(self, mock_bot_class):
        """Тест регистрации пользователя"""
        from src.bot.telegram_bot import TelegramHRBot
        
        # Создание экземпляра бота
        bot_instance = TelegramHRBot(app)
        
        # Симуляция команды /start
        bot_instance.handle_start_command(self.mock_message)
        
        # Проверка создания пользователя
        user = User.query.filter_by(telegram_id=123456789).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'test_user')
    
    def test_job_search_functionality(self):
        """Тест функциональности поиска вакансий"""
        # Создание тестовых данных
        employer = User(telegram_id=111, username='emp', role='employer')
        db.session.add(employer)
        
        jobs = [
            Job(title='Python Developer', description='Python job', company='Company A', 
                location='Москва', skills='Python', employer_id=111),
            Job(title='Java Developer', description='Java job', company='Company B', 
                location='СПб', skills='Java', employer_id=111),
            Job(title='Frontend Developer', description='React job', company='Company C', 
                location='Москва', skills='React', employer_id=111)
        ]
        
        db.session.add_all(jobs)
        db.session.commit()
        
        # Тест поиска по ключевому слову
        python_jobs = Job.query.filter(Job.title.contains('Python')).all()
        self.assertEqual(len(python_jobs), 1)
        self.assertEqual(python_jobs[0].title, 'Python Developer')
        
        # Тест поиска по локации
        moscow_jobs = Job.query.filter(Job.location == 'Москва').all()
        self.assertEqual(len(moscow_jobs), 2)
    
    def test_notification_system(self):
        """Тест системы уведомлений"""
        # Создание пользователя с подпиской
        user = User(telegram_id=444, username='notif_user', role='candidate')
        subscription = Subscription(
            user_id=444,
            keywords='Python',
            location='Москва',
            frequency='immediate'
        )
        
        db.session.add_all([user, subscription])
        db.session.commit()
        
        # Создание вакансии, которая должна вызвать уведомление
        employer = User(telegram_id=555, username='emp2', role='employer')
        job = Job(
            title='Senior Python Developer',
            description='Отличная возможность для Python разработчика',
            company='Новая Компания',
            location='Москва',
            employer_id=555
        )
        
        db.session.add_all([employer, job])
        db.session.commit()
        
        # Проверка, что вакансия соответствует подписке
        matching_jobs = Job.query.filter(
            Job.title.contains('Python'),
            Job.location == 'Москва'
        ).all()
        
        self.assertEqual(len(matching_jobs), 1)
        self.assertEqual(matching_jobs[0].title, 'Senior Python Developer')

class TestDatabasePerformance(unittest.TestCase):
    """Тестирование производительности базы данных"""
    
    def setUp(self):
        """Настройка тестового окружения"""
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        """Очистка после тестов"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_bulk_data_operations(self):
        """Тест операций с большим объемом данных"""
        import time
        
        # Создание работодателя
        employer = User(telegram_id=999, username='bulk_emp', role='employer')
        db.session.add(employer)
        db.session.commit()
        
        # Массовое создание вакансий
        start_time = time.time()
        
        jobs = []
        for i in range(100):
            job = Job(
                title=f'Test Job {i}',
                description=f'Description for job {i}',
                company=f'Company {i % 10}',
                location='Москва' if i % 2 == 0 else 'СПб',
                salary_min=50000 + (i * 1000),
                salary_max=100000 + (i * 1000),
                employer_id=999
            )
            jobs.append(job)
        
        db.session.add_all(jobs)
        db.session.commit()
        
        creation_time = time.time() - start_time
        
        # Тест поиска
        start_time = time.time()
        moscow_jobs = Job.query.filter(Job.location == 'Москва').all()
        search_time = time.time() - start_time
        
        # Проверки
        self.assertEqual(len(moscow_jobs), 50)  # Половина вакансий в Москве
        self.assertLess(creation_time, 5.0)  # Создание должно занимать менее 5 секунд
        self.assertLess(search_time, 1.0)   # Поиск должен занимать менее 1 секунды
        
        print(f"Время создания 100 вакансий: {creation_time:.2f} сек")
        print(f"Время поиска по локации: {search_time:.2f} сек")

def run_database_health_check():
    """Проверка состояния базы данных"""
    print("🔍 Проверка состояния базы данных...")
    
    try:
        with app.app_context():
            # Проверка подключения (исправлено для новой версии SQLAlchemy)
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            print("✅ Подключение к PostgreSQL: OK")
            
            # Проверка таблиц
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            expected_tables = ['users', 'jobs', 'applications', 'subscriptions']
            
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Таблица {table}: OK")
                else:
                    print(f"❌ Таблица {table}: ОТСУТСТВУЕТ")
            
            # Проверка индексов
            with db.engine.connect() as connection:
                result = connection.execute(db.text("""
                    SELECT indexname FROM pg_indexes 
                    WHERE tablename IN ('users', 'jobs', 'applications', 'subscriptions')
                """))
                
                indexes = [row[0] for row in result]
                print(f"📊 Найдено индексов: {len(indexes)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False

def run_bot_integration_test():
    """Интеграционный тест бота"""
    print("🤖 Запуск интеграционного теста бота...")
    
    try:
        from src.bot.telegram_bot import TelegramHRBot
        
        # Создание экземпляра бота с тестовым токеном (исправлено)
        with patch('telebot.TeleBot') as mock_telebot:
            bot_instance = TelegramHRBot(app, app)  # Передаем app дважды
            print("✅ Инициализация бота: OK")
            
            # Тест обработчиков команд
            mock_message = Mock()
            mock_message.from_user.id = 12345
            mock_message.from_user.username = 'test'
            mock_message.from_user.first_name = 'Test'
            mock_message.chat.id = 12345
            mock_message.text = '/start'
            
            # Симуляция команды /start
            bot_instance.handle_start_command(mock_message)
            print("✅ Обработка команды /start: OK")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка тестирования бота: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Запуск тестов Telegram HR Bot с PostgreSQL")
    print("=" * 60)
    
    # Проверка состояния базы данных
    db_ok = run_database_health_check()
    print()
    
    # Интеграционный тест бота
    bot_ok = run_bot_integration_test()
    print()
    
    if db_ok and bot_ok:
        print("🧪 Запуск unit тестов...")
        print("-" * 40)
        
        # Запуск unit тестов
        unittest.main(argv=[''], exit=False, verbosity=2)
        
        print("\n✅ Все тесты завершены!")
    else:
        print("❌ Предварительные проверки не пройдены. Исправьте ошибки перед запуском тестов.")
        sys.exit(1)

