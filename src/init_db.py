import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core import logger, db
from user import User

def init_db(db):
    try:
        # Создаем таблицы
        User.metadata.create_all(db.engine)
        Vacancy.metadata.create_all(db.engine)
        Candidate.metadata.create_all(db.engine)
        logger.info("База данных успешно инициализирована.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")

