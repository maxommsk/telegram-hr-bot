@echo off
echo Получение обновлений с GitHub...
git fetch origin
git pull origin master
echo Активация виртуального окружения...
call venv\Scripts\activate
echo Обновление зависимостей...
pip install -r requirements.txt
echo Обновление завершено!
pause
