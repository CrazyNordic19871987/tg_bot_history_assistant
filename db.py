import sqlite3

DATABASE_NAME = 'history_bot.db'

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Таблица для викторины с баллами
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        score INTEGER DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()

init_db()
print("База данных создана успешно.")
