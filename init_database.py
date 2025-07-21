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

# --- Настройка ---
# Добавляем путь к папке src, чтобы Python мог найти ваши модули
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
# Загружаем переменные окружения из .env файла
load_dotenv()
# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_db_url():
    """Собирает URL для подключения к БД из переменных окружения."""
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_host = os.getenv('POSTGRES_HOST')
    db_port = os.getenv('POSTGRES_PORT')
    db_name = os.getenv('POSTGRES_DB')

    if not all([db_user, db_password, db_host, db_port, db_name]):
        logger.error("Критическая ошибка: не все переменные окружения для подключения к БД установлены!")
        raise ValueError("Не установлены переменные окружения для подключения к базе данных")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def init_db():
    """
    Основная функция для создания таблиц.
    Она импортирует Base и модели, а затем вызывает create_all.
    """
    try:
        # --- ИСПРАВЛЕННЫЙ ИМПОРТ BASE ---
        # Поскольку Base в src/__init__.py, мы импортируем его так:
        from __init__ import Base

        # --- ИСПРАВЛЕННЫЙ ИМПОРТ МОДЕЛЕЙ ---
        # Поскольку все модели лежат "плоско" в src, импортируем их напрямую.
        # Это нужно, чтобы SQLAlchemy "узнал" о них перед вызовом create_all.
        import user
        import job
        import subscription
        # ... и так далее, если есть другие файлы с моделями

        engine = create_engine(get_db_url())

        logger.info("Подключение к базе данных...")
        with engine.connect() as connection:
            version_result = connection.execute(text("SELECT version()"))
            logger.info(f"Версия PostgreSQL: {version_result.scalar_one()}")

        logger.info("Создание таблиц на основе моделей SQLAlchemy...")
        # Это главная команда. Она создает все таблицы, о которых "знает" Base.
        Base.metadata.create_all(bind=engine)

        logger.info("✅ Все таблицы успешно созданы!")
        return True

    except ImportError as e:
        logger.error(f"Критическая ошибка импорта: не удалось найти модели. Проверьте пути. Ошибка: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Критическая ошибка при инициализации базы данных: {e}", exc_info=True)
        return False


def main():
    """Главная функция скрипта."""
    print("🚀 Инициализация базы данных HR Bot (на основе моделей SQLAlchemy)")
    print("=" * 60)
    
    if init_db():
        print("✅ Инициализация завершена успешно!")
    else:
        print("❌ Инициализация завершена с ошибками! Проверьте логи выше.")
        sys.exit(1)


if __name__ == "__main__":
    main()
