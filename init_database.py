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
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_host = os.getenv('POSTGRES_HOST')
    db_port = os.getenv('POSTGRES_PORT')
    db_name = os.getenv('POSTGRES_DB')
    
    if not all([db_user, db_password, db_host, db_port, db_name]):
        logger.error("Не все переменные окружения для подключения к БД установлены!")
        raise ValueError("Database environment variables not set")
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def init-то импортированы до вызова create_all.
        from database.models import Base
        
        # --- ВАЖНО: Убедитесь, что ваши модели импортируются ---
        # Обычно это делается в файле, где определен Base (например, в database/models/__init__.py)
        # Если ваши модели лежат в отдельных файлах (например, src/models/user.py),
        # и они нигде не импортируются все вместе, их нужно импортировать здесь,
        # чтобы SQLAlchemy о них "узнал".
        # Пример:
        # import models.user
        # import models.job
        # import models.subscription
        # import models.job_application
        # import models.job_favorite
        # import models.user_resume
        # import models.notification
        # import models.user_statistic

        database_url = get_database_url()
        engine = create_engine(database_url)
        
        logger.info("Подключение к базе данных установлено.")
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))create_all(engine)
        
        logger.info("✅ Все таблицы успешно созданы!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}", exc_info=True)
        return False

de
