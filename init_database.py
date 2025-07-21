#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных HR Bot
Создает все необходимые таблицы на основе моделей SQLAlchemy.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (важно для локального запуска)
load_dotenv()

# Добавляем путь к src, чтобы можно было импортировать модели
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """Получает URL подключения к базе данных из переменных окружения"""
    db_name = os.getenv('POSTGRES_DB')
    
    if not all([db_user, db_password, db_host, db_port, db_name]):
        logger.error("Не все переменные окружения для подключения к БД установлены!")
        raise ValueError("Database environment variables not set")
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def init_database():
    """
    Инициализирует базу данных, создавая все таблицы на основе импортированных моделей.
    """
    try:
        # Импортируем базовый класс и все модели здесь, чтобы они были зарегистрированы
        from database.models import Base
        # Убедитесь, что все ваши модели импортированы где-то, чтобы Base их "увидел"
        # Например, если у вас есть models/user.py, models/job.py и т.д.
        # и они импортируются в database/models/__init__.py, этого достаточно.
        # Если нет, их нужно импортировать явно:
        import models.user
        import models.            result = connection.execute(text("SELECT version();"))
            logger.info(f"PostgreSQL версия: {result.fetchone()[0]}")
        
        logger.info("Создание всех таблиц на основе моделей SQLAlchemy...")
        
        # Эта команда - ключ ко всему. Она создает таблицы по Python-моделям.
        Base.metadata.create_all(engine)
        
        logger.info("✅ Все таблицы успешно созданы!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}", exc_info=True)
        return False

def main():
    """Главная функция"""
    print("🚀 Инициализация базы данных HR Bot (на основе моделей SQLAlchemy)")
    print("=" * 60)
    success = init_database()
    print("=" * 60)
    if success:
        print("✅ Инициализация завершена успешно!")
    else:
        print("❌ Инициализация завершена с ошибками!")
        sys.exit(1)

if __name__ == "__main__":
    main()
