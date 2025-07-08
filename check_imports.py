print("=== Проверка импортов ===")

# Проверка основных модулей
try:
    from main import app
    print("✅ main.py: OK")
except Exception as e:
    print(f"❌ main.py: FAILED - {e}")

try:
    from user import User, db
    print("✅ user.py: OK")
except Exception as e:
    print(f"❌ user.py: FAILED - {e}")

try:
    from job import Job
    print("✅ job.py: OK")
except Exception as e:
    print(f"❌ job.py: FAILED - {e}")

try:
    from application import Application
    print("✅ application.py: OK")
except Exception as e:
    print(f"❌ application.py: FAILED - {e}")

try:
    from subscription import Subscription
    print("✅ subscription.py: OK")
except Exception as e:
    print(f"❌ subscription.py: FAILED - {e}")

try:
    from telegram_bot import TelegramHRBot
    print("✅ telegram_bot.py: OK")
except Exception as e:
    print(f"❌ telegram_bot.py: FAILED - {e}")

try:
    from scheduler import NotificationScheduler
    print("✅ scheduler.py: OK")
except Exception as e:
    print(f"❌ scheduler.py: FAILED - {e}")

