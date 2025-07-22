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
                
                # Попытка найти классы моделей
                logger.info("Ищем классы моделей в модулях...")
                for module_name, module in [('user', user), ('application', application), ('job', job), ('subscription', subscription)]:
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if hasattr(attr, '__tablename__'):
                            logger.info(f"Найден класс модели: {module_name}.{attr_name} -> таблица '{attr.__tablename__}'")
            
            logger.info("Создание всех таблиц...")
            db.create_all()
            logger.info("✅ Команда db.create_all() выполнена!")
            
            # Проверяем, что действительно создалось
            logger.info("Проверяем созданные таблицы в базе...")
            
            # ИСПРАВЛЕНО: Используем text() для SQL-запроса
            from sqlalchemy import text
            result = db.session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            actual_tables = [row[0] for row in result.fetchall()]
            logger.info(f"Реальные таблицы в базе: {actual_tables}")
            
            # Дополнительная проверка основных таблиц
            required_tables = ['users', 'jobs', 'subscriptions', 'applications']
            found_tables = []
            missing_tables = []
            
            for table in required_tables:
                if table in actual_tables:
                    found_tables.append(table)
                    logger.info(f"✅ Таблица '{table}' найдена")
                else:
                    missing_tables.append(table)
                    logger.warning(f"❌ Таблица '{table}' не найдена")
            
            # Итоговый отчет
            logger.info(f"📊 Статистика таблиц:")
            logger.info(f"   Найдено: {len(found_tables)} из {len(required_tables)}")
            logger.info(f"   Найденные: {found_tables}")
            if missing_tables:
                logger.warning(f"   Отсутствующие: {missing_tables}")
            
            # Проверяем версию PostgreSQL
            try:
                result = db.session.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                logger.info(f"🐘 PostgreSQL: {version.split(',')[0]}")
            except Exception as e:
                logger.warning(f"Не удалось получить версию PostgreSQL: {e}")
            
            # Проверяем общее количество таблиц
            try:
                result = db.session.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
                total_tables = result.fetchone()[0]
                logger.info(f"📋 Общее количество таблиц в схеме public: {total_tables}")
            except Exception as e:
                logger.warning(f"Не удалось подсчитать общее количество таблиц: {e}")

    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        logger.error("Проверьте, что все модули находятся в папке src/")
        logger.error("Структура должна быть:")
        logger.error("  src/")
        logger.error("    core.py")
        logger.error("    user.py")
        logger.error("    job.py")
        logger.error("    application.py")
        logger.error("    subscription.py")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        import traceback
        logger.error("Полная трассировка ошибки:")
        traceback.print_exc()
        sys.exit(1)

    logger.info("🎉 Инициализация завершена успешно!")

def check_environment():
    """Проверяет переменные окружения"""
    logger.info("🔍 Проверка переменных окружения...")
    
    required_vars = ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Скрываем пароль в логах
            display_value = "***" if "PASSWORD" in var else value
            logger.info(f"✅ {var}: {display_value}")
        else:
            missing_vars.append(var)
            logger.error(f"❌ {var}: не установлена")
    
    if missing_vars:
        logger.error(f"Отсутствующие переменные: {missing_vars}")
        return False
    
    return True

def main():
    """Главная функция с проверками"""
    print("🚀 Инициализация базы данных HR Bot")
    print("=" * 50)
    
    # Проверяем переменные окружения
    if not check_environment():
        logger.error("❌ Не все переменные окружения установлены!")
        sys.exit(1)
    
    # Проверяем структуру файлов
    logger.info("📁 Проверка структуры файлов...")
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    required_files = ['core.py', 'user.py', 'job.py', 'application.py', 'subscription.py']
    
    for file in required_files:
        file_path = os.path.join(src_path, file)
        if os.path.exists(file_path):
            logger.info(f"✅ {file}")
        else:
            logger.warning(f"❌ {file} - не найден")
    
    # Запускаем инициализацию
    initialize_database()
    
    print("=" * 50)
    print("✅ Скрипт завершен успешно!")
    print("🎯 Теперь можно запускать основное приложение!")

if __name__ == "__main__":
    main()
