# main.py
import os
from threading import Thread
from flask import jsonify
from waitress import serve

# Импортируем все из нашего центрального файла core.py
from core import app, engine, logger
# Импортируем только функцию init_db
from init_db import init_db
# Импортируем классы бота и планировщика
from telegram_bot import TelegramHRBot
from scheduler import NotificationScheduler

# 1. Инициализируем БД
init_db()

# 2. Создаем бота
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
telegram_bot = TelegramHRBot(token=bot_token, db_engine=engine) if bot_token else None

# 3. Создаем и запускаем планировщик (если он нужен)
# scheduler = NotificationScheduler(telegram_bot)
# scheduler_thread = Thread(target=scheduler.run, daemon=True)
# scheduler_thread.start()
# logger.info("Планировщик запущен.")

# --- Роуты Flask ---
@app.route('/')
def index(): return "HR Bot is running!"

@app.route('/api/health')
def health_check():
    try:
        engine.connect().close()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error"}), 503

# --- Точка входа ---
if __name__ == '__main__':
    if telegram_bot:
        logger.info("Запуск Telegram бота...")
        bot_thread = Thread(target=telegram_bot.run_polling, kwargs={'drop_pending_updates': True}, daemon=True)
        bot_thread.start()

    port = int(os.getenv('PORT', 5000))
    logger.info(f"Запуск Flask приложения на порту {port}")
    serve(app, host='0.0.0.0', port=port)
