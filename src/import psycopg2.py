import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def check_database_health():
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'telegram_hr_bot'),
            user=os.getenv('POSTGRES_USER', 'hr_bot_user1'),
            password=os.getenv('POSTGRES_PASSWORD', 'Maximka1992')
        )
        cursor = conn.cursor()
        
        # Проверка подключения
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        # Статистика таблиц
        cursor.execute("""
        SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
        FROM pg_stat_user_tables;
        """)
        print("\nTable statistics:")
        for row in cursor.fetchall():
            print(f"  {row[1]}: {row[2]} inserts, {row[3]} updates, {row[4]} deletes")
        
        # Размер базы данных
        cursor.execute("""
        SELECT pg_size_pretty(pg_database_size(current_database()));
        """)
        size = cursor.fetchone()
        print(f"\nDatabase size: {size[0]}")
        
        cursor.close()
        conn.close()
        print(f"\nDatabase health check completed at {datetime.now()}")
        return True
        
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False

if __name__ == "__main__":
    check_database_health()

