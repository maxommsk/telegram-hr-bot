import os
from threading import Thread
from flask import Flask, jsonify
from dotenv import load_dotenv
from telegram_bot import TelegramHRBot
from scheduler import NotificationScheduler
from init_db import init_db, engine

# ДОБАВИТЬ ЭТОТ БЛОК
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

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

init_db()

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
if not bot_token:
    logger.warning("Telegram Bot Token не настроен. Бот не будет запущен.")
    telegram_bot = None
else:
    telegram_bot = TelegramHRBot(token=bot_token, db_engine=engine)

scheduler = NotificationScheduler(telegram_bot)

@app.route('/')
def index():
    return "HR Bot is running!"

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        connection = engine.connect()
        connection.close()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error", "database": "disconnected"}), 503

if __name__ == '__main__':
    if telegram_bot:
        logger.info("Запуск Telegram бота в отдельном потоке...")
        bot_thread = Thread(target=telegram_bot.run_polling, kwargs={'drop_pending_updates': True})
        bot_thread.daemon = True
        bot_thread.start()

    logger.info("Запуск планировщика уведомлений в отдельном потоке...")
    scheduler_thread = Thread(target=scheduler.run)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    port = int(os.getenv('PORT', 5000))
    logger.info(f"Запуск Flask приложения на порту {port}")
    
    try:
        from waitress import serve
        serve(app, host='0.0.0.0', port=port)
    except ImportError:
        logger.warning("Waitress не установлен. Запуск в режиме разработки Flask. Не для продакшена!")
        app.run(host='0.0.0.0', port=port)

