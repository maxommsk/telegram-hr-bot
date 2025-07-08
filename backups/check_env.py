from dotenv import load_dotenv
import os

load_dotenv()

print("=== Проверка переменных окружения ===")
print(f"Bot token: {'OK' if os.getenv('TELEGRAM_BOT_TOKEN') else 'MISSING'}")
print(f"DB host: {'OK' if os.getenv('POSTGRES_HOST') else 'MISSING'}")
print(f"DB name: {'OK' if os.getenv('POSTGRES_DB') else 'MISSING'}")
print(f"DB user: {'OK' if os.getenv('POSTGRES_USER') else 'MISSING'}")
print(f"DB password: {'OK' if os.getenv('POSTGRES_PASSWORD') else 'MISSING'}")

# Показать значения (без пароля)
print("\n=== Текущие значения ===")
print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST', 'НЕ УСТАНОВЛЕНО')}")
print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB', 'НЕ УСТАНОВЛЕНО')}")
print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER', 'НЕ УСТАНОВЛЕНО')}")
print(f"TELEGRAM_BOT_TOKEN: {'УСТАНОВЛЕН' if os.getenv('TELEGRAM_BOT_TOKEN') else 'НЕ УСТАНОВЛЕН'}")

