#!/bin/bash
set -e

echo "🔧 Установка systemd сервиса для Telegram HR Bot..."

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Этот скрипт должен запускаться с правами root (sudo )"
    exit 1
fi

# Создание директории для проекта в /opt
PROJECT_DIR="/opt/telegram-hr-bot"
echo "📁 Создание директории проекта: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"

# Копирование файлов проекта
echo "📋 Копирование файлов проекта..."
cp -r ./* "$PROJECT_DIR/"
chown -R root:root "$PROJECT_DIR"

# Установка systemd сервиса
echo "⚙️ Установка systemd сервиса..."
cp telegram-hr-bot.service /etc/systemd/system/
systemctl daemon-reload

# Включение автозапуска
echo "🚀 Включение автозапуска сервиса..."
systemctl enable telegram-hr-bot.service

echo "✅ Установка завершена!"
echo ""
echo "Доступные команды:"
echo "  sudo systemctl start telegram-hr-bot    # Запустить сервис"
echo "  sudo systemctl stop telegram-hr-bot     # Остановить сервис"
echo "  sudo systemctl status telegram-hr-bot   # Проверить статус"
echo "  sudo systemctl restart telegram-hr-bot  # Перезапустить сервис"
echo "  sudo journalctl -u telegram-hr-bot -f   # Просмотр логов в реальном времени"
