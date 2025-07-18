# init_db.py
from core import app, db
# ИСПРАВЬТЕ ЭТУ СТРОКУ: импортируйте ваши модели из правильного файла (например, 'user')
from user import User #, Vacancy, Candidate (добавьте все ваши модели)

def init_db():
    """Создает все таблицы в базе данных."""
    try:
        with app.app_context():
            db.create_all()
        logger.info("База данных успешно инициализирована.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")
