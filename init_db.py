import sqlite3

# Name of your SQLite database file
DATABASE = 'database.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        ''')
        conn.commit()
        print("Database initialized and 'users' table created (if it didn't exist).")

if __name__ == '__main__':
    init_db()
