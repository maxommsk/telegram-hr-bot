import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core import engine, logger
from user import User

# Инициализация сессии
Session = sessionmaker(bind=engine)

def init_db():
    try:
        # Создаем таблицы
        User.metadata.create_all(engine)
        Vacancy.metadata.create_all(engine)
        Candidate.metadata.create_all(engine)
        logger.info("База данных успешно инициализирована.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")

