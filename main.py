# main.py
import os
from threading import Thread
from flask import jsonify
from waitress import serve

# Импортируем все из нашего центрального файла
from core import app, engine, logger
from init_db import init_db
from telegram_bot import TelegramHRBot
from scheduler import NotificationScheduler

# 1. Инициализируем БД
init_db()

# 2. Создаем бота
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
telegram_bot = TelegramHRBot(token=bot_token, db_engine=engine) if bot_token else None

# 3. Создаем планировщик (теперь он не зависит от main)
scheduler = NotificationScheduler(telegram_bot)

# --- Роуты Flask ---
@app.route('/')
def index(): return "HR Bot is running!"

@app.route('/api/health')
def health_check():
    # ... код health_check ...

# --- Точка входа ---
if __name__ == '__main__':
    if telegram_bot:
        logger.info("Запуск Telegram бота...")
        bot_thread = Thread(target=telegram_bot.run_polling, kwargs={'drop_pending_updates': True}, daemon=True)
        bot_thread.start()

    logger.info("Запуск планировщика...")
    scheduler_thread = Thread(target=scheduler.run, daemon=True)
    scheduler_thread.start()

    port = int(os.getenv('PORT', 5000))
    logger.info(f"Запуск Flask приложения на порту {port}")
    serve(app, host='0.0.0.0', port=port)
