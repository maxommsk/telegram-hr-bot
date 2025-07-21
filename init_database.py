#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных для Flask-приложения.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Добавляем корневую папку проекта в путь Python
sys.path.append(os.path.dirname(__file__))

# Загружаем переменные окружения из файла .env
load_dotenv()

# ИСПРАВЛЕНИЕ: импортируем модели из правильных файлов
from src.user import *

# Настраиваем систему логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_database():
    """
    Основная функция для инициализации базы данных.
    """
    logger.info("🚀 Запуск скрипта инициализации базы данных...")
    
    try:
        logger.info("Импортируем 'app' и 'db' из 'src.main'...")
        from src.main import app, db
        logger.info("Импорт 'app' и 'db' успешно завершен.")

        logger.info("Модели пользователей импортированы из src.user")

        with app.app_context():
            logger.info("Вход в контекст приложения Flask.")
            
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
            logger.info(f"Используется URI базы данных: {db_uri}")

            logger.info("Выполняется команда db.create_all() для создания таблиц...")
            db.create_all()
            
            logger.info("✅ Команда db.create_all() успешно выполнена.")

    except Exception as e:
        logger.error(f"❌ Произошла непредвиденная ошибка во время инициализации БД.")
        logger.error(f"   Текст системной ошибки: {e}", exc_info=True)
        sys.exit(1)

    logger.info("🎉 Инициализация базы данных успешно завершена!")


if __name__ == "__main__":
    initialize_database()
