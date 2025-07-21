#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных для Flask-приложения.
Создает все таблицы на основе моделей, зарегистрированных в db.Model.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# --- Настройка ---
# Добавляем путь к папке src, чтобы Python мог найти ваше приложение
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """
    Главная функция.
    Импортирует Flask-приложение, создает контекст и вызывает db.create_all().
    """
    print("🚀 Инициализация базы данных для Flask-приложения...")
    print("=" * 60)

    try:
        # --- КЛЮЧЕВОЙ МОМЕНТ ---
        # Мы импортируем ваше основное приложение и объект `db` из него.
        # Замените 'application' на имя файла, где создается `app = Flask(__name__)`.
        # Замените 'db' на имя вашей переменной SQLAlchemy, если она называется иначе.
        from main import app, db

        # Flask-SQLAlchemy требует, чтобы операции с базой данных
        # выполнялись внутри "контекста приложения".
        with app.app_context():
            logger.info("Создание всех таблиц на основе моделей Flask-SQLAlchemy...")
            
            # Эта команда - аналог Base.metadata.create_all(engine)
            # Она найдет все классы, которые наследуются от db.Model, и создаст для них таблицы.
            db.create_all()
            
            logger.info("✅ Все таблицы успешно созданы!")

        print("✅ Инициализация завершена успешно!")

    except ImportError as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА ИМПОРТА: Не удалось импортировать 'app' или 'db'.")
        logger.error(f"   Убедитесь, что в файле 'src/application.py' есть 'app = Flask(...)' и 'db = SQLAlchemy(app)'.")
        logger.error(f"   Текст ошибки: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Инициализация завершена с ошибками! Ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
