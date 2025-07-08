import sqlite3

def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_message(username, message):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (username, message) VALUES (?, ?)', (username, message))
    conn.commit()
    conn.close()
