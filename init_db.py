from db import get_conn

def init_db():

    db = get_conn()   

    cursor = db.cursor()

    # users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # favorites
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        code TEXT,
        name TEXT,
        UNIQUE(user_id, code)
    )
    """)

    # prices
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_code TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,
        UNIQUE(stock_code, date)
    )
    """)

    # trades（売買ログ）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        stock_code TEXT,
        buy_date TEXT,
        buy_price REAL,
        sell_date TEXT,
        sell_price REAL,
        profit REAL,
        memo TEXT
    )
    """)

    # tags
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    # taggings（紐付け）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS taggings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trade_id INTEGER,
        tag_id INTEGER
    )
    """)

    db.commit()
    db.close()
