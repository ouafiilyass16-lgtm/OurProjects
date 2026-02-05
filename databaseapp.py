import sqlite3
import os

def init_db():
    os.makedirs("instance", exist_ok=True)

    db_path = os.path.abspath("instance/parkingData.db")
    print("📁 BASE CRÉÉE ICI :", db_path)

    db = sqlite3.connect(db_path)
    cr = db.cursor()

    cr.execute("""
    CREATE TABLE IF NOT EXISTS utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT,
        admin_auth INTEGER DEFAULT 0,
        gardien_auth INTEGER DEFAULT 0
    )
    """)

    cr.execute("""
    CREATE TABLE IF NOT EXISTS places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        libre INTEGER DEFAULT 1
    )
    """)

    db.commit()
    db.close()
