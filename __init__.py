# init_db.py
from sqlalchemy.orm import declarative_base
from core import engine # Импортируем engine из нового файла core.py

Base = declarative_base()

def init_db():
    # Импортируем все модели здесь, чтобы они зарегистрировались в Base
    # Убедитесь, что у вас есть файл models.py или папка models
    # Если модели в разных файлах, их нужно импортировать здесь.
    # Например: from user import User
    Base.metadata.create_all(bind=engine)

