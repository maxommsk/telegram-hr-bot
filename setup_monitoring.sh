#!/bin/bash
set -e

echo "🔧 Настройка системы мониторинга..."

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Этот скрипт должен запускаться с правами root (sudo)"
    exit 1
fi

# Копирование скрипта мониторинга
echo "📋 Копирование скрипта мониторинга..."
cp health_monitor.sh /usr/local/bin/
chmod +x /usr/local/bin/health_monitor.sh

# Создание лог файла
echo "📝 Создание лог файла..."
touch /var/log/telegram-hr-bot-monitor.log
chmod 644 /var/log/telegram-hr-bot-monitor.log

# Настройка logrotate для ротации логов
echo "🔄 Настройка ротации логов..."
cat > /etc/logrotate.d/telegram-hr-bot << 'EOF'
/var/log/telegram-hr-bot-monitor.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF

# Добавление в crontab для проверки каждые 5 минут
echo "⏰ Настройка cron задачи..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/health_monitor.sh") | crontab -

# Добавление ежедневного бэкапа БД
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/telegram-hr-bot/backup_db.sh") | crontab -

echo "✅ Мониторинг настроен!"
echo ""
echo "Настроенные задачи:"
echo "  - Проверка здоровья каждые 5 минут"
echo "  - Автоматический бэкап БД каждый день в 02:00"
echo "  - Ротация логов каждый день"
echo ""
echo "Просмотр логов мониторинга:"
echo "  tail -f /var/log/telegram-hr-bot-monitor.log"
