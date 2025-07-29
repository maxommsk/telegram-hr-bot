#!/bin/bash
set -e

HEALTH_URL="http://localhost:5000/api/health"
MAX_RETRIES=3
RETRY_DELAY=10
LOG_FILE="/var/log/telegram-hr-bot-monitor.log"

# Функция логирования
log_message( ) {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_message "🔍 Starting health check..."

# Проверка health endpoint
for i in $(seq 1 $MAX_RETRIES); do
    if curl -f -s --connect-timeout 10 --max-time 30 "$HEALTH_URL" > /dev/null 2>&1; then
        log_message "✅ Health check passed (attempt $i/$MAX_RETRIES)"
        exit 0
    else
        log_message "❌ Health check failed (attempt $i/$MAX_RETRIES)"
        if [ $i -lt $MAX_RETRIES ]; then
            log_message "⏳ Waiting $RETRY_DELAY seconds before retry..."
            sleep $RETRY_DELAY
        fi
    fi
done

# Если все попытки неудачны - перезапускаем сервис
log_message "🚨 All health checks failed, restarting service..."

# Проверка статуса контейнеров
log_message "📊 Checking container status..."
docker-compose -f /opt/telegram-hr-bot/docker-compose.production.yml ps >> "$LOG_FILE" 2>&1

# Перезапуск сервиса
log_message "🔄 Restarting telegram-hr-bot service..."
systemctl restart telegram-hr-bot.service

# Ожидание запуска
sleep 30

# Финальная проверка
if curl -f -s --connect-timeout 10 --max-time 30 "$HEALTH_URL" > /dev/null 2>&1; then
    log_message "✅ Service restarted successfully"
else
    log_message "❌ Service restart failed - manual intervention required"
    # Отправка уведомления (можно настроить email/telegram)
fi
