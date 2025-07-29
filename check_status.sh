#!/bin/bash

echo "🔍 Проверка статуса Telegram HR Bot..."
echo ""

# Проверка systemd сервиса
echo "📊 Статус systemd сервиса:"
sudo systemctl status telegram-hr-bot.service --no-pager -l

echo ""
echo "🐳 Статус Docker контейнеров:"
docker-compose -f /opt/telegram-hr-bot/docker-compose.production.yml ps

echo ""
echo "🏥 Health check приложения:"
if curl -f -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Приложение работает нормально"
else
    echo "❌ Приложение недоступно"
fi

echo ""
echo "📝 Последние логи (последние 10 строк ):"
sudo journalctl -u telegram-hr-bot.service -n 10 --no-pager
