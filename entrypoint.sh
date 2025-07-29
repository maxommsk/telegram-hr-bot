#!/bin/sh
set -e

echo "🚀 Production Entrypoint: Starting Telegram HR Bot..."

# Проверка обязательных переменных окружения
required_vars="TELEGRAM_BOT_TOKEN POSTGRES_HOST POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB"
for var in $required_vars; do
    if [ -z "$(eval echo \$$var)" ]; then
        echo "❌ Error: Required environment variable $var is not set"
        exit 1
    fi
done

# Ожидание готовности БД (если файл check_db.py существует)
if [ -f "src/check_db.py" ]; then
    echo "⏳ Waiting for database..."
    python src/check_db.py
fi

# Инициализация БД
echo "🔧 Initializing database..."
python src/init_database.py

echo "✅ Starting main application..."
exec python src/main.py
