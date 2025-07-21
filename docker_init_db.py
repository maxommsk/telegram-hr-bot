#!/usr/bin/env python3
"""
Упрощенный скрипт инициализации БД для Docker
Использует SQLAlchemy модели для создания таблиц
"""

import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_db_with_models():
    """Инициализирует БД используя SQLAlchemy модели"""
    try:
        # Собираем строку подключения к БД из переменных окружения
        db_user = os.getenv('POSTGRES_USER')
        db_password = os.getenv('POSTGRES_PASSWORD')
        db_host = os.getenv('POSTGRES_HOST')
        db_port = os.getenv('POSTGRES_PORT')
        db_name = os.getenv('POSTGRES_DB')

        # Проверяем, что все переменные загружены
        if not all([db_user, db_password, db_host, db_port, db_name]):
            logger.error("Переменные окружения для подключения к БД не установлены!")
            return False

        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        logger.info(f"Подключение к БД: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")

        # Создаем engine
        engine = create_engine(database_url)
        
        # Импортируем модели
        try:
            from user import User, db as user_db
            from job import Job
            from subscription import Subscription
            logger.info("Модели успешно импортированы")
        except ImportError as e:
            logger.error(f"Ошибка импорта моделей: {e}")
            logger.info("Попытка создания таблиц через SQL...")
            return create_tables_with_sql(engine)
        
        # Создаем все таблицы
        try:
            # Если используется Flask-SQLAlchemy
            if hasattr(user_db, 'metadata'):
                user_db.metadata.create_all(engine)
                logger.info("✅ Таблицы созданы через Flask-SQLAlchemy")
            else:
                # Если используется обычная SQLAlchemy
                from sqlalchemy.ext.declarative import declarative_base
                Base = declarative_base()
                Base.metadata.create_all(engine)
                logger.info("✅ Таблицы созданы через SQLAlchemy")
                
        except Exception as e:
            logger.error(f"Ошибка создания таблиц через модели: {e}")
            logger.info("Попытка создания таблиц через SQL...")
            return create_tables_with_sql(engine)
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        return False

def create_tables_with_sql(engine):
    """Создает таблицы через прямые SQL команды"""
    try:
        from sqlalchemy import text
        
        sql_commands = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                phone_number VARCHAR(20),
                email VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                description TEXT NOT NULL,
                company VARCHAR(255) NOT NULL,
                location VARCHAR(255),
                salary_min INTEGER,
                salary_max INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                is_remote BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                search_criteria JSONB NOT NULL DEFAULT '{}',
                frequency VARCHAR(20) NOT NULL DEFAULT 'daily',
                is_active BOOLEAN DEFAULT TRUE,
                is_paused BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_notification_sent TIMESTAMP
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
            CREATE INDEX IF NOT EXISTS idx_jobs_active ON jobs(is_active);
            CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
            """
        ]
        
        with engine.connect() as connection:
            for sql in sql_commands:
                connection.execute(text(sql))
            connection.commit()
        
        logger.info("✅ Базовые таблицы созданы через SQL")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка создания таблиц через SQL: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Инициализация БД для Docker...")
    success = init_db_with_models()
    
    if success:
        print("✅ Инициализация завершена успешно!")
    else:
        print("❌ Ошибка инициализации!")
        sys.exit(1)
