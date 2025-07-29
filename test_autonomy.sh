#!/bin/bash
set -e

echo "🧪 Тестирование автономной работы Telegram HR Bot"
echo "================================================"
echo ""

# Проверка всех необходимых файлов
echo "📋 Проверка файлов конфигурации..."
required_files=(
    "Dockerfile.production"
    "docker-compose.production.yml" 
    ".env.production"
    "entrypoint.sh"
    "telegram-hr-bot.service"
    "deploy.sh"
    "backup_db.sh"
    "update.sh"
    "health_monitor.sh"
    "setup_monitoring.sh"
    "install_service.sh"
    "check_status.sh"
    "system_info.sh"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    else
        echo "✅ $file"
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo ""
    echo "❌ Отсутствуют файлы:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    echo ""
    echo "Создайте недостающие файлы перед продолжением."
    exit 1
fi

echo ""
echo "✅ Все необходимые файлы присутствуют!"
echo ""

# Проверка .env.production
echo "🔧 Проверка конфигурации .env.production..."
if [ -f ".env.production" ]; then
    required_vars=("TELEGRAM_BOT_TOKEN" "POSTGRES_HOST" "POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env.production; then
            missing_vars+=("$var")
        else
            echo "✅ $var настроен"
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo ""
        echo "❌ В .env.production отсутствуют переменные:"
        for var in "${missing_vars[@]}"; do
            echo "   - $var"
        done
        echo ""
        echo "Добавьте недостающие переменные в .env.production"
        exit 1
    fi
else
    echo "❌ Файл .env.production не найден!"
    exit 1
fi

echo ""
echo "✅ Конфигурация .env.production корректна!"
echo ""

# Тест сборки Docker образа
echo "🐳 Тестирование сборки Docker образа..."
if docker build -f Dockerfile.production -t telegram-hr-bot:test . > /dev/null 2>&1; then
    echo "✅ Docker образ собирается успешно"
    docker rmi telegram-hr-bot:test > /dev/null 2>&1
else
    echo "❌ Ошибка сборки Docker образа"
    exit 1
fi

echo ""
echo "🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!"
echo ""
echo "📋 Следующие шаги для развертывания в Яндекс Облаке:"
echo ""
echo "1. Загрузите проект на ваш сервер в Яндекс Облаке:"
echo "   scp -r ./* user@your-server:/home/user/telegram-hr-bot/"
echo ""
echo "2. На сервере выполните установку:"
echo "   cd /home/user/telegram-hr-bot"
echo "   sudo ./install_service.sh"
echo "   sudo ./setup_monitoring.sh"
echo ""
echo "3. Запустите сервис:"
echo "   sudo systemctl start telegram-hr-bot"
echo ""
echo "4. Проверьте статус:"
echo "   ./check_status.sh"
echo ""
echo "5. Для проверки автономности перезагрузите сервер:"
echo "   sudo reboot"
echo "   # После перезагрузки бот должен запуститься автоматически"
echo ""
echo "🔍 Полезные команды для мониторинга:"
echo "   ./system_info.sh                              # Системная информация"
echo "   sudo journalctl -u telegram-hr-bot -f         # Логи в реальном времени"
echo "   tail -f /var/log/telegram-hr-bot-monitor.log  # Логи мониторинга"
echo "   docker logs hr_bot_app_prod -f                # Логи приложения"
echo ""
echo "✅ Ваш Telegram HR Bot готов к автономной работе!"
