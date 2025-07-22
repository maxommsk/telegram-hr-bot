#!/usr/bin/env python3
"""
Отладочный скрипт для инициализации базы данных.
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
        # Импортируем напрямую из core.py
        logger.info("Импортируем app и db напрямую из core...")
        from core import app, db
        
        # Принудительно импортируем все модели
        logger.info("Импортируем все модели...")
        import user
        import application  
        import job
        import subscription
        
        with app.app_context():
            logger.info("Проверяем зарегистрированные модели...")
            
            # Выводим все зарегистрированные таблицы
            tables = list(db.metadata.tables.keys())
            logger.info(f"Найденные модели/таблицы: {tables}")
            
            if not tables:
                logger.warning("⚠️ Не найдено ни одной модели!")
                logger.info("Проверяем импортированные классы...")
                logger.info(f"user модуль: {dir(user)}")
                logger.info(f"application модуль: {dir(application)}")
                logger.info(f"job модуль: {dir(job)}")
                logger.info(f"subscription модуль: {dir(subscription)}")
            
            logger.info("Создание всех таблиц...")
            db.create_all()
            logger.info("✅ Команда db.create_all() выполнена!")
            
            # Проверяем, что действительно создалось
            logger.info("Проверяем созданные таблицы в базе...")
            result = db.session.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            actual_tables = [row[0] for row in result]
            logger.info(f"Реальные таблицы в базе: {actual_tables}")

    except Exception as e:
        logger.error(f"❌ Ошибка: {e}", exc_info=True)
        sys.exit(1)

    logger.info("🎉 Инициализация завершена!")

if __name__ == "__main__":
    initialize_database()
