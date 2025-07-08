import os
import sys
import threading
import logging
from dotenv import load_dotenv

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Загружаем переменные окружения
load_dotenv()

from flask import Flask, send_from_directory
from flask_cors import CORS
from user import db
from telegram_bot import TelegramHRBot
from scheduler import NotificationScheduler

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/telegram_hr_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Создание директории для логов
os.makedirs('logs', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Конфигурация Flask
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your_super_secret_key_here_change_in_production')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB

# Конфигурация PostgreSQL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Формируем URL из отдельных параметров
    postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')
    postgres_db = os.getenv('POSTGRES_DB', 'telegram_hr_bot')
    postgres_user = os.getenv('POSTGRES_USER', 'hr_bot_user')
    postgres_password = os.getenv('POSTGRES_PASSWORD', 'secure_password_here')
    
    database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 20,
    'max_overflow': 0
}

# Включаем CORS для API
CORS(app, origins="*")

# Регистрируем blueprints
#app.register_blueprint(user_bp, url_prefix='/api')

# Инициализация базы данных
db.init_app(app)

# Глобальные переменные для бота и планировщика
telegram_bot = None
notification_scheduler = None

def create_tables():
    """Создает таблицы в базе данных"""
    with app.app_context():
        try:
            # Импортируем все модели для создания таблиц
            from user import User
            from job import Job
            from application import Application
            from subscription import Subscription
            
            db.create_all()
            logger.info("Таблицы базы данных созданы успешно")
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")

def init_telegram_bot():
    """Инициализирует Telegram бота"""
    global telegram_bot
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token or bot_token == 'YOUR_BOT_TOKEN_HERE':
        logger.warning("Telegram Bot Token не настроен. Бот не будет запущен.")
        return None
    
    try:
        telegram_bot = TelegramHRBot(bot_token, app)
        logger.info("Telegram бот инициализирован успешно")
        return telegram_bot
    except Exception as e:
        logger.error(f"Ошибка при инициализации Telegram бота: {e}")
        return None

def init_notification_scheduler():
    """Инициализирует планировщик уведомлений"""
    global notification_scheduler
    
    if not telegram_bot:
        logger.warning("Telegram бот не инициализирован. Планировщик уведомлений не будет запущен.")
        return None
    
    notification_enabled = os.getenv('NOTIFICATION_ENABLED', 'true').lower() == 'true'
    if not notification_enabled:
        logger.info("Уведомления отключены в конфигурации")
        return None
    
    try:
        notification_scheduler = NotificationScheduler(telegram_bot, app)
        logger.info("Планировщик уведомлений инициализирован успешно")
        return notification_scheduler
    except Exception as e:
        logger.error(f"Ошибка при инициализации планировщика уведомлений: {e}")
        return None

def start_telegram_bot():
    """Запускает Telegram бота в отдельном потоке"""
    if telegram_bot:
        try:
            logger.info("Запуск Telegram бота...")
            telegram_bot.start_polling()
        except Exception as e:
            logger.error(f"Ошибка при запуске Telegram бота: {e}")

def start_notification_scheduler():
    """Запускает планировщик уведомлений в отдельном потоке"""
    if notification_scheduler:
        try:
            logger.info("Запуск планировщика уведомлений...")
            notification_scheduler.start()
        except Exception as e:
            logger.error(f"Ошибка при запуске планировщика уведомлений: {e}")

# Webhook endpoint для Telegram (опционально)
@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик webhook для Telegram"""
    if telegram_bot:
        return telegram_bot.handle_webhook()
    return "Bot not initialized", 503

# API endpoint для статистики
@app.route('/api/stats')
def get_stats():
    """Возвращает статистику системы"""
    try:
        from user import User
        from job import Job
        from application import Application
        from subscription import Subscription
        
        stats = {
            'users_total': User.query.count(),
            'users_employers': User.query.filter_by(user_type='employer').count(),
            'users_jobseekers': User.query.filter_by(user_type='jobseeker').count(),
            'jobs_total': Job.query.count(),
            'jobs_active': Job.query.filter_by(is_active=True).count(),
            'applications_total': Application.query.count(),
            'subscriptions_total': Subscription.query.count(),
            'subscriptions_active': Subscription.query.filter_by(is_active=True, is_paused=False).count()
        }
        return stats
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        return {'error': 'Database not available'}, 503

# Статические файлы и SPA роутинг
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    logger.info("Запуск Telegram HR Bot...")
    
    # Создаем таблицы
    create_tables()
    
    # Инициализируем компоненты
    init_telegram_bot()
    init_notification_scheduler()
    
    # Запускаем Telegram бота в отдельном потоке
    if telegram_bot:
        bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
        bot_thread.start()
    
    # Запускаем планировщик уведомлений в отдельном потоке
    if notification_scheduler:
        scheduler_thread = threading.Thread(target=start_notification_scheduler, daemon=True)
        scheduler_thread.start()
    
    # Запускаем Flask приложение
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Запуск Flask приложения на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)
