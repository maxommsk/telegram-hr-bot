# main.py
import os
import sys
from threading import Thread
from flask import jsonify
from waitress import serve

sys.path.append(os.path.dirname(__file__))

# ИЗМЕНЕНИЕ 1: Импортируем 'db' вместо 'engine'
from core import app, db, logger
from init_db import init_db
from telegram_bot import TelegramHRBot
from scheduler import NotificationScheduler

# Инициализируем БД в контексте приложения
with app.app_context():
    init_db(db)

# ИЗМЕНЕНИЕ 2: Передаем 'db' в конструктор бота
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
telegram_bot = None
if bot_token and ':' in bot_token:
    telegram_bot = TelegramHRBot(token=bot_token, db=db, flask_app=app)
else:
    logger.warning("TELEGRAM_BOT_TOKEN отсутствует или некорректен - бот не будет запущен")

# ... (остальной код без изменений до health_check)

@app.route('/api/health')
def health_check():
    try:
        # ИЗМЕНЕНИЕ 3: Проверяем подключение через db.engine
        with db.engine.connect() as connection:
            connection.execute('SELECT 1')
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error"}), 503

# ... (остальной код без изменений)
if __name__ == '__main__':
    if telegram_bot:
        logger.info("Запуск Telegram бота...")
        # Убедитесь, что метод называется 'run'
        bot_thread = Thread(target=telegram_bot.run, kwargs={'drop_pending_updates': True}, daemon=True)
        bot_thread.start()

    port = int(os.getenv('PORT', 5000))
    logger.info(f"Запуск Flask приложения на порту {port}")
    serve(app, host='0.0.0.0', port=port)
