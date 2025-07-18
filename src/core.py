# core.py
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # <--- ИМПОРТИРУЕМ РАСШИРЕНИЕ
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Правильная инициализация ---
app = Flask(__name__)
db = SQLAlchemy() # <--- Создаем объект SQLAlchemy

# Конфигурируем Flask-приложение
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

if not all([db_user, db_password, db_host, db_port, db_name]):
    logger.error("Ключевые переменные окружения для подключения к БД не установлены!")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Связываем SQLAlchemy с нашим приложением
# ЭТОТ ШАГ ИСПРАВЛЯЕТ ОШИБКУ
db.init_app(app)

