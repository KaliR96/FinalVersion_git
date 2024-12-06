import sqlite3


def init_database():
    query = """
    CREATE TABLE IF NOT EXISTS user_analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id BIGINT,
        username TEXT,
        state TEXT,
        event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_new BOOLEAN
    );
    """
    conn = sqlite3.connect("bot_data.db")  # Подключение к базе
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()

# Подключение к базе данных
def connect_db():
    conn = sqlite3.connect("bot_data.db")
    return conn

# Функция для выполнения запроса
async def execute_query(query, params=()):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

# Функция для получения данных
async def fetch_all(query, params=()):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results
