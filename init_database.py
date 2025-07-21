#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных HR Bot.
Создает все таблицы на основе моделей SQLAlchemy.
Этот скрипт должен быть максимально независимым.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, declarative_base
from dotenv import load_dotenv

# --- Настройка ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()
# Добавляем путь к src, чтобы найти модули
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def get_db_url():
    """Собирает URL для подключения к БД из переменных окружения."""
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_host = os.getenv('POSTGRES_HOST')
    db_port = os.getenv('POSTGRES_PORT')
    db_name = os.getenv('POSTGRES_DB')

    if not all([db_user, db_password, db_host, db_port, db_name]):
        logger.error("Критическая ошибка: не все переменные окружения для БД установлены!")
        raise ValueError("Не установлены переменные окружения для базы данных")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def main():
    """Главная функция скрипта."""
    print("🚀 Инициализация базы данных HR Bot")
    print("=" * 60)

    try:
        # --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ ---
        # Мы создаем Base прямо здесь, вместо того чтобы импортировать его.
        Base = declarative_base()

        # Теперь импортируем все ваши модели.
        # Они должны быть написаны так, чтобы наследовать Base, который мы создали выше.
        # Это может потребовать небольшого исправления в самих моделях.
        import user
        import job
        import subscription
        # ... и все остальные ваши модели

        engine = create_engine(get_db_url())

        logger.info("Создание всех таблиц на основе моделей...")
        Base.metadata.create_all(bind=engine)

        print("✅ Инициализация завершена успешно!")

    except Exception as e:
        logger.error(f"❌ Инициализация завершена с ошибками! Ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
