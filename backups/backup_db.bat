@'
@echo off
set PGPASSWORD=Maximka1992
set BACKUP_DIR=%~dp0backups
set DATE=%date:~-4,4%%date:~-10,2%%date:~-7,2%
set TIME=%time:~0,2%%time:~3,2%%time:~6,2%
set FILENAME=telegram_hr_bot_%DATE%_%TIME%.sql

"C:\Program Files\PostgreSQL\17\bin\pg_dump" -U hr_bot_user1 -h localhost telegram_hr_bot > "%BACKUP_DIR%\%FILENAME%"

echo Backup created: %FILENAME%
pause
'@ | Out-File -FilePath "backup_db.bat" -Encoding ASCII