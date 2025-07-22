from core import logger, db

# Импортируем модели, чтобы они зарегистрировались в метаданных SQLAlchemy
from user import User  # noqa: F401
from job import Job  # noqa: F401
from application import Application  # noqa: F401
from subscription import Subscription  # noqa: F401


def init_db(db):
        """Создает все таблицы, определённые моделями."""
    try:
              db.create_all()

        logger.info("База данных успешно инициализирована.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")

