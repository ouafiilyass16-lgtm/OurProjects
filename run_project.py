# run_project.py
import os
import subprocess
import sys
import sqlite3
from pathlib import Path

# 1. Créer le dossier instance si nécessaire
Path("instance").mkdir(exist_ok=True)


# 2. Initialiser la base de données avec des utilisateurs de TEST
def init_db():
    conn = sqlite3.connect("instance/parking.db")
    cr = conn.cursor()

    # Créer les tables si elles n'existent pas
    cr.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cr.execute("""
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            libre INTEGER DEFAULT 1
        )
    """)

    cr.execute("""
        CREATE TABLE IF NOT EXISTS tarifs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prix_par_heure REAL DEFAULT 10.0
        )
    """)

    # Insérer des utilisateurs de TEST (pas besoin d'inscription !)
    try:
        cr.execute("INSERT OR IGNORE INTO utilisateurs (nom, email, password, role) VALUES (?, ?, ?, ?)",
                   ("Admin Test", "admin@parking.com", "admin", "Admin"))
        cr.execute("INSERT OR IGNORE INTO utilisateurs (nom, email, password, role) VALUES (?, ?, ?, ?)",
                   ("Gardien Test", "gardien@parking.com", "gardien", "Gardien"))
        cr.execute("INSERT OR IGNORE INTO utilisateurs (nom, email, password, role) VALUES (?, ?, ?, ?)",
                   ("Client Test", "client@parking.com", "client", "Client"))

        # Insérer des places de parking
        for i in range(1, 11):
            nom = f"A{i}" if i <= 4 else (f"B{i - 4}" if i <= 8 else f"C{i - 8}")
            cr.execute("INSERT OR IGNORE INTO places (nom, libre) VALUES (?, ?)", (nom, 1 if i % 2 == 0 else 0))

        # Insérer le tarif
        cr.execute("INSERT OR IGNORE INTO tarifs (prix_par_heure) VALUES (10.0)")

        conn.commit()
        print("Base de données initialisée avec succès")
        print("   Identifiants de test :")
        print("   - Admin: admin@parking.com / admin")
        print("   - Gardien: gardien@parking.com / gardien")
        print("   - Client: client@parking.com / client")
    except Exception as e:
        print(f"⚠️  Erreur DB: {e}")
    finally:
        conn.close()


# 3. Lancer Flask
if __name__ == "__main__":
    init_db()
    print("\nLancement de l'application SmartPark...")
    print("   Accédez à: http://127.0.0.1:3000/login\n")

    # Lancer Flask avec Python directement (évite les erreurs Windows)
    subprocess.run([sys.executable, "-m", "flask", "run", "--port=3000", "--debug"])