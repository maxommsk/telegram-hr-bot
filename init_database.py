#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных HR Bot
Создает все необходимые таблицы в PostgreSQL
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_database_url():
    """Получает URL подключения к базе данных из переменных окружения"""
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_host = os.getenv('POSTGRES_HOST')
    db_port = os.getenv('POSTGRES_PORT')
    db_name = os.getenv('POSTGRES_DB')
    
    if not all([db_user, db_password, db_host, db_port, db_name]):
        logger.error("Не все переменные окружения для подключения к БД установлены!")
        logger.error(f"POSTGRES_USER: {'✓' if db_user else '✗'}")
        logger.error(f"POSTGRES_PASSWORD: {'✓' if db_password else '✗'}")
        logger.error(f"POSTGRES_HOST: {'✓' if db_host else '✗'}")
        logger.error(f"POSTGRES_PORT: {'✓' if db_port else '✗'}")
        logger.error(f"POSTGRES_DB: {'✓' if db_name else '✗'}")
        raise ValueError("Database environment variables not set")
    
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    logger.info(f"Подключение к БД: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
    
    return database_url

def create_tables_sql():
    """Возвращает SQL для создания всех таблиц"""
    return """
    -- Создание таблицы пользователей
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE NOT NULL,
        username VARCHAR(255),
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        phone_number VARCHAR(20),
        email VARCHAR(255),
        is_active BOOLEAN DEFAULT TRUE,
        is_admin BOOLEAN DEFAULT FALSE,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        preferred_language VARCHAR(10) DEFAULT 'ru',
        notification_settings JSONB DEFAULT '{}',
        profile_data JSONB DEFAULT '{}'
    );

    -- Создание таблицы вакансий
    CREATE TABLE IF NOT EXISTS jobs (
        id SERIAL PRIMARY KEY,
        title VARCHAR(500) NOT NULL,
        description TEXT NOT NULL,
        company VARCHAR(255) NOT NULL,
        location VARCHAR(255),
        salary_min INTEGER,
        salary_max INTEGER,
        currency VARCHAR(10) DEFAULT 'RUB',
        employment_type VARCHAR(50),
        experience_level VARCHAR(50),
        skills TEXT,
        requirements TEXT,
        benefits TEXT,
        contact_info TEXT,
        external_url VARCHAR(1000),
        source VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE,
        is_featured BOOLEAN DEFAULT FALSE,
        is_remote BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        views_count INTEGER DEFAULT 0,
        applications_count INTEGER DEFAULT 0,
        metadata JSONB DEFAULT '{}'
    );

    -- Создание таблицы подписок
    CREATE TABLE IF NOT EXISTS subscriptions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        search_criteria JSONB NOT NULL DEFAULT '{}',
        frequency VARCHAR(20) NOT NULL DEFAULT 'daily',
        is_active BOOLEAN DEFAULT TRUE,
        is_paused BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_notification_sent TIMESTAMP,
        notifications_sent_count INTEGER DEFAULT 0,
        max_notifications_per_day INTEGER DEFAULT 10,
        min_salary INTEGER,
        only_remote BOOLEAN DEFAULT FALSE,
        only_featured BOOLEAN DEFAULT FALSE,
        company_blacklist TEXT,
        exclude_keywords TEXT,
        expires_at TIMESTAMP
    );

    -- Создание таблицы откликов на вакансии
    CREATE TABLE IF NOT EXISTS job_applications (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
        status VARCHAR(50) DEFAULT 'pending',
        cover_letter TEXT,
        resume_data JSONB,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        employer_response TEXT,
        notes TEXT,
        UNIQUE(user_id, job_id)
    );

    -- Создание таблицы избранных вакансий
    CREATE TABLE IF NOT EXISTS job_favorites (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, job_id)
    );

    -- Создание таблицы резюме пользователей
    CREATE TABLE IF NOT EXISTS user_resumes (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        title VARCHAR(255) NOT NULL,
        content JSONB NOT NULL DEFAULT '{}',
        is_active BOOLEAN DEFAULT TRUE,
        is_default BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        file_path VARCHAR(500),
        file_type VARCHAR(20)
    );

    -- Создание таблицы уведомлений
    CREATE TABLE IF NOT EXISTS notifications (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        type VARCHAR(50) NOT NULL,
        title VARCHAR(255) NOT NULL,
        message TEXT NOT NULL,
        data JSONB DEFAULT '{}',
        is_read BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        read_at TIMESTAMP
    );

    -- Создание таблицы статистики
    CREATE TABLE IF NOT EXISTS user_statistics (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        date DATE NOT NULL,
        jobs_viewed INTEGER DEFAULT 0,
        jobs_applied INTEGER DEFAULT 0,
        searches_performed INTEGER DEFAULT 0,
        notifications_received INTEGER DEFAULT 0,
        UNIQUE(user_id, date)
    );

    -- Создание индексов для оптимизации
    CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
    CREATE INDEX IF NOT EXISTS idx_jobs_active ON jobs(is_active);
    CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
    CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
    CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
    CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
    CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(is_active, is_paused);
    CREATE INDEX IF NOT EXISTS idx_job_applications_user_id ON job_applications(user_id);
    CREATE INDEX IF NOT EXISTS idx_job_applications_job_id ON job_applications(job_id);
    CREATE INDEX IF NOT EXISTS idx_job_favorites_user_id ON job_favorites(user_id);
    CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
    CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read);
    """

def init_database():
    """Инициализирует базу данных, создавая все необходимые таблицы"""
    try:
        # Получаем URL подключения
        database_url = get_database_url()
        
        # Создаем подключение
        engine = create_engine(database_url)
        
        logger.info("Подключение к базе данных установлено")
        
        # Проверяем подключение
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info(f"PostgreSQL версия: {version}")
        
        # Создаем таблицы
        logger.info("Создание таблиц...")
        
        with engine.connect() as connection:
            # Выполняем SQL для создания таблиц
            connection.execute(text(create_tables_sql()))
            connection.commit()
        
        logger.info("✅ Все таблицы успешно созданы!")
        
        # Проверяем созданные таблицы
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"Созданные таблицы: {', '.join(tables)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        return False

def check_tables():
    """Проверяет существование всех необходимых таблиц"""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        expected_tables = [
            'users', 'jobs', 'subscriptions', 'job_applications',
            'job_favorites', 'user_resumes', 'notifications', 'user_statistics'
        ]
        
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            
            existing_tables = [row[0] for row in result.fetchall()]
            
            logger.info("Проверка таблиц:")
            for table in expected_tables:
                status = "✅" if table in existing_tables else "❌"
                logger.info(f"  {status} {table}")
            
            missing_tables = set(expected_tables) - set(existing_tables)
            if missing_tables:
                logger.warning(f"Отсутствующие таблицы: {', '.join(missing_tables)}")
                return False
            else:
                logger.info("✅ Все необходимые таблицы существуют!")
                return True
                
    except Exception as e:
        logger.error(f"Ошибка при проверке таблиц: {e}")
        return False

def main():
    """Главная функция"""
    print("🚀 Инициализация базы данных HR Bot")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        # Режим проверки таблиц
        print("📋 Проверка существующих таблиц...")
        success = check_tables()
    else:
        # Режим создания таблиц
        print("🔨 Создание таблиц в базе данных...")
        success = init_database()
        
        if success:
            print("\n📋 Проверка созданных таблиц...")
            check_tables()
    
    print("=" * 50)
    if success:
        print("✅ Инициализация завершена успешно!")
    else:
        print("❌ Инициализация завершена с ошибками!")
        sys.exit(1)

if __name__ == "__main__":
    main()
