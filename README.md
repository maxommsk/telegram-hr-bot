# Telegram HR Bot - Production Deployment

## 🚀 Автономное развертывание в Яндекс Облаке

Этот проект настроен для полностью автономной работы в облачной среде без необходимости ручного вмешательства.

### 📋 Что изменено для автономной работы:

1. ✅ **Замена Windows-скриптов** - все .bat файлы заменены на .sh
2. ✅ **Production Dockerfile** - без auto_restart.py для стабильной работы
3. ✅ **Systemd сервис** - автоматический запуск при загрузке системы
4. ✅ **Health monitoring** - автоматическая проверка и перезапуск при сбоях
5. ✅ **Логирование** - централизованные логи с ротацией
6. ✅ **Автоматические бэкапы** - ежедневное резервное копирование БД

### 🛠️ Развертывание на сервере:

```bash
# 1. Загрузка проекта
scp -r ./* user@your-server:/opt/telegram-hr-bot/

# 2. Установка на сервере
cd /opt/telegram-hr-bot
sudo ./install_service.sh
sudo ./setup_monitoring.sh

# 3. Запуск
sudo systemctl start telegram-hr-bot
