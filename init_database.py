#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных для Flask-приложения.

Этот скрипт импортирует экземпляр приложения Flask и объект SQLAlchemy,
создает контекст приложения и затем вызывает db.create_all() для создания
всех таблиц на основе определенных моделей.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# --- Начальная настройка ---

# Добавляем папку 'src' в путь Python, чтобы можно было импортировать 'main' и 'models'.
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Загружаем переменные окружения из файла .env
load_dotenv()

# Настраиваем логирование для вывода информативных сообщений.
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
        # --- Импорт приложения и моделей ---
        logger.info("Импортируем 'app' и 'db' из 'src.main'...")
        from main import app, db
        logger.info("Импорт 'app' и 'db' успешно завершен.")

        # ======================================================================
        # --- КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ ---
        # Явно импортируем все классы из файла с моделями (src/models.py).
        # Это необходимо, чтобы Flask-SQLAlchemy "узнал" о существовании
        # ваших моделей перед тем, как пытаться создать для них таблицы.
        logger.info("Принудительно импортируем все модели из 'src.models'...")
        from models import *
        logger.info("Все известные модели импортированы.")
        # ======================================================================

        # --- Создание контекста и таблиц ---
        with app.app_context():
            logger.info("Вход в контекст приложения Flask.")
            
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
            logger.info(f"Используется URI базы данных: {db_uri}")

            logger.info("Выполняется команда db.create_all() для создания таблиц...")
            db.create_all()
            
            logger.info("✅ Команда db.create_all() успешно выполнена.")

    except ImportError as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось импортировать 'app', 'db' или 'models'.")
        logger.error(f"   Проверьте, что файлы 'src/main.py' и 'src/models.py' существуют и корректны.")
        logger.error(f"   Текст системной ошибки: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Произошла непредвиденная ошибка во время инициализации БД.")
        logger.error(f"   Текст системной ошибки: {e}", exc_info=True)
        sys.exit(1)

    logger.info("🎉 Инициализация базы данных успешно завершена!")


if __name__ == "__main__":
    initialize_database()
