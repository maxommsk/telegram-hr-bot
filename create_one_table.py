import os
from sqlalchemy import create_engine, text

# Получаем URL из переменных окружения
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

print(f"Подключаюсь к: {database_url}")

try:
    engine = create_engine(database_url)
    with engine.connect() as connection:
        print("Соединение установлено. Пытаюсь создать одну таблицу 'test_table'...")
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                message TEXT
            );
        """))
        connection.commit()
        print("Команда на создание таблицы выполнена.")

    print("Скрипт завершен.")

except Exception as e:
    print(f"Произошла ошибка: {e}")

