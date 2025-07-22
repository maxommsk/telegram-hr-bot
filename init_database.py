#!/usr/bin/env python3
"""
Простой скрипт для инициализации базы данных.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Добавляем папку src в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_database():
    logger.info("🚀 Запуск скрипта инициализации базы данных...")
    
    try:
        # Импортируем напрямую из core.py, минуя main.py
        logger.info("Импортируем app и db напрямую из core...")
        from core import app, db
        
        # Принудительно импортируем все модели
        logger.info("Импортируем все модели...")
        import user
        import application  
        import job
        import subscription
        
        with app.app_context():
            logger.info("Создание всех таблиц...")
            db.create_all()
            logger.info("✅ Все таблицы созданы!")

    except Exception as e:
        logger.error(f"❌ Ошибка: {e}", exc_info=True)
        sys.exit(1)

    logger.info("🎉 Инициализация завершена!")

if __name__ == "__main__":
    initialize_database()
