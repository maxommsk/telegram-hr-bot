@echo off
echo Деплой на Яндекс.Облако...

echo Проверка конфигурации Yandex Cloud CLI...
yc config list

echo Сборка и загрузка образа...
docker build -t cr.yandex/%YC_REGISTRY_ID%/hr-bot:latest .
docker push cr.yandex/%YC_REGISTRY_ID%/hr-bot:latest

echo Деплой на сервер...
ssh hr-bot@%SERVER_HOST% "cd /opt/hr-bot && sudo docker-compose -f docker-compose.production.yml pull && sudo docker-compose -f docker-compose.production.yml up -d"

echo Деплой завершен!
pause
