# core.py
import os
import logging
from flask import Flask
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# 1. Настраиваем логгер
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 2. Создаем Flask приложение
app = Flask(__name__)

# 3. Создаем подключение к БД (engine)
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

if not all([db_user, db_password, db_host, db_port, db_name]):
    logger.error("Ключевые переменные окружения для подключения к БД не установлены!")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL)

# Конфигурируем Flask приложение для работы с SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
