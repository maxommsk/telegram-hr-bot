@echo off
echo Синхронизация с GitHub...
git add .
set /p commit_message="Введите сообщение коммита: "
git commit -m "%commit_message%"
git push origin master
echo Синхронизация завершена!
pause