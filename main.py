import os
from threading import Thread
from flask import Flask, jsonify
from dotenv import load_dotenv
from application import logger  # Убедитесь, что у вас есть application/__init__.py с настройкой логгера
from telegram_bot import TelegramHRBot
from scheduler import NotificationScheduler
from database import init_db, engine  # Убедитесь, что engine импортируется из вашего модуля базы данных

# Загружаем переменные окружения из .env файла
load_dotenv()

# --- Инициализация основных компонентов ---

# 1. Flask приложение
app = Flask(__name__)

# 2. База данных
# Собираем строку подключения к БД из переменных окружения
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

if not all([db_user, db_password, db_host, db_port, db_name]):
    logger.error("Ключевые переменные окружения для подключения к БД не установлены!")
    # В реальном приложении здесь лучше выбросить исключение
    # raise ValueError("Database environment variables not set")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Эта строка нужна, чтобы SQLAlchemy знала о нашем URL
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализируем таблицы
init_db()

# 3. Telegram Бот
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
if not bot_token:
    logger.warning("Telegram Bot Token не настроен. Бот не будет запущен.")
    telegram_bot = None
else:
    # Создаем ЕДИНСТВЕННЫЙ экземпляр бота
    telegram_bot = TelegramHRBot(token=bot_token, db_engine=engine)

# 4. Планировщик
scheduler = NotificationScheduler(telegram_bot)


# --- Роуты Flask ---

@app.route('/')
def index():
    return "HR Bot is running!"

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for Docker and other monitoring systems.
    """
    try:
        connection = engine.connect()
        connection.close()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error", "database": "disconnected"}), 503


# --- Точка входа для запуска ---

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    if telegram_bot:
        logger.info("Запуск Telegram бота в отдельном потоке...")
        # Здесь мы передаем в поток МЕТОД нашего экземпляра бота
        bot_thread = Thread(target=telegram_bot.run_polling, kwargs={'drop_pending_updates': True})
        bot_thread.daemon = True  # Поток завершится, когда завершится основной процесс
        bot_thread.start()

    # Запускаем планировщик в отдельном потоке
    logger.info("Запуск планировщика уведомлений в отдельном потоке...")
    scheduler_thread = Thread(target=scheduler.run)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Запускаем Flask приложение в основном потоке
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Запуск Flask приложения на порту {port}")
    # Используем более подходящий для продакшена WSGI сервер, например, waitress
    from waitress import serve
    serve(app, host='0.0.0.0', port=port)

```**Ключевые изменения:**
1.  Создается **один** экземпляр `TelegramHRBot`.
2.  В поток `bot_thread` передается **метод этого экземпляра** (`telegram_bot.run_polling`), а не сторонняя функция.
3.  Я добавил `drop_pending_updates=True` прямо в вызов потока.
4.  Я добавил `daemon = True` для потоков, чтобы они корректно завершались вместе с основным процессом.
5.  Я заменил `app.run` на `waitress.serve`, который лучше подходит для продакшена. Для этого нужно добавить `waitress` в ваш `requirements.txt`.

**Что еще нужно сделать:**
1.  **Добавьте `waitress` в ваш файл `requirements.txt`.** Просто откройте его и допишите `waitress` в конец.
2.  Вам нужно немного изменить `telegram_bot.py`, чтобы он принимал `db_engine` при инициализации.

    **Откройте `telegram_bot.py` и измените `__init__`:**

    **Было:**
    ```python
    def __init__(self, token, db_url=None):
        # ...
    ```
    **Стало:**
    ```python
    def __init__(self, token, db_engine):
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.engine = db_engine  # Используем переданный engine
        self.Session = sessionmaker(bind=self.engine)
        self._setup_handlers()
    ```
    Это позволит нам использовать один и тот же `engine` во всем приложении.

После этих двух правок (в `main.py` и `telegram_bot.py`) и добавления `waitress` в `requirements.txt`, сохраните все в GitHub и выполните стандартную процедуру пересборки и перезапуска на сервере. Это должно решить проблему на фундаментальном уровне.
