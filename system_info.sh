#!/bin/bash

echo "🖥️  Системная информация Telegram HR Bot"
echo "========================================"
echo ""

echo "📅 Дата и время:"
date
echo ""

echo "💾 Использование диска:"
df -h | grep -E "(Filesystem|/dev/)"
echo ""

echo "🧠 Использование памяти:"
free -h
echo ""

echo "⚡ Загрузка системы:"
uptime
echo ""

echo "🐳 Docker контейнеры:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "📊 Статус systemd сервиса:"
systemctl status telegram-hr-bot.service --no-pager -l
echo ""

echo "🌐 Сетевые подключения:"
netstat -tlnp | grep :5000 || echo "Порт 5000 не прослушивается"
echo ""

echo "📝 Последние логи приложения:"
docker logs hr_bot_app_prod --tail 10 2>/dev/null || echo "Контейнер приложения не найден"
echo ""

echo "🔍 Последние логи мониторинга:"
tail -10 /var/log/telegram-hr-bot-monitor.log 2>/dev/null || echo "Лог мониторинга не найден"
