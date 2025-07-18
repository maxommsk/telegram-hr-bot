# main.py
import os
from threading import Thread
from flask import jsonify

# Импортируем наши центральные компоненты из core.py
from core import app, engine, logger
from init_db import init_db
from telegram_bot import TelegramHRBot
from scheduler import NotificationScheduler

# Инициализируем таблицы в базе данных
init_db()

# --- Инициализация компонентов ---
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
if not bot_token:
    logger.warning("Telegram Bot Token не настроен. Бот не будет запущен.")
    telegram_bot = None
else:
    telegram_bot = TelegramHRBot(token=bot_token, db_engine=engine)

# Передаем экземпляр бота в планировщик
scheduler = NotificationScheduler(telegram_bot)

# --- Роуты Flask ---
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

# --- Точка входа для запуска ---
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

