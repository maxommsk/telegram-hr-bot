# init_db.py
from sqlalchemy.orm import declarative_base
from core import engine

Base = declarative_base()

def init_db(app=None):
    """Инициализирует базу данных, создавая все таблицы."""
    # Импортируем все модели здесь, чтобы они зарегистрировались в Base
    # Если у вас есть файлы с моделями, импортируйте их здесь
    # Например: from user import User
    Base.metadata.create_all(bind=engine)
