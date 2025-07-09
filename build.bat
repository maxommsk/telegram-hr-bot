@echo off
echo Сборка Docker образа для продакшена...

set /p version="Введите версию (например, 1.0.0): "

docker build -t hr-bot:%version% .
docker tag hr-bot:%version% hr-bot:latest

echo Образ собран: hr-bot:%version%
pause
