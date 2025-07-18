from main import app
from user import db, User
from job import Job
from application import Application
from subscription import Subscription
from sqlalchemy.orm import declarative_base
from core import engine

Base = declarative_base()
def init_db():
    # Здесь должны быть импорты ваших моделей, чтобы SQLAlchemy о них узнал
    # Например: from models.user import User
    # Если у вас нет отдельного файла/папки для моделей, их нужно импортировать здесь.
    Base.metadata.create_all(bind=engine)


with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")
