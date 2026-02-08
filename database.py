import sqlite3
import os
from datetime import datetime

DB_PATH = "instance/parking.db"
os.makedirs("instance", exist_ok=True)


def init_db():
    db = sqlite3.connect(DB_PATH)
    cr = db.cursor()

    # Utilisateurs
    cr.execute("""
    CREATE TABLE IF NOT EXISTS utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT,
        admin_auth INTEGER DEFAULT 1,
        gardien_auth INTEGER DEFAULT 1
    )
    """)
    cr.execute(
        "INSERT OR IGNORE INTO utilisateurs (id, nom, email, password, role, admin_auth, gardien_auth) VALUES (1, 'Admin', 'admin@parking.com', 'admin', 'Admin', 1, 1)")
    cr.execute(
        "INSERT OR IGNORE INTO utilisateurs (id, nom, email, password, role, admin_auth, gardien_auth) VALUES (2, 'Gardien', 'gardien@parking.com', 'gardien', 'Gardien', 1, 1)")

    # Véhicules
    cr.execute("""
    CREATE TABLE IF NOT EXISTS vehicules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matricule TEXT,
        marque TEXT,
        couleur TEXT,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES utilisateurs(id)ON DELETE CASCADE
    )
    """)

    # Places
    cr.execute("""
    CREATE TABLE IF NOT EXISTS places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        libre INTEGER DEFAULT 1
    )
    """)

    # Tickets
    cr.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        vehicule_id INTEGER,
        place_id INTEGER,
        date_entree TEXT,
        date_sortie TEXT,
        montant REAL,
        autorise INTEGER DEFAULT 0,  -- 0: non autorisé, 1: autorisé
        FOREIGN KEY(user_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
        FOREIGN KEY(vehicule_id) REFERENCES vehicules(id)ON DELETE CASCADE,
        FOREIGN KEY(place_id) REFERENCES places(id)ON DELETE CASCADE
    )
    """)

    # Vérifier si la colonne autorise existe déjà (migration si nécessaire)
    try:
        cr.execute("SELECT autorise FROM tickets LIMIT 1")
    except sqlite3.OperationalError:
        cr.execute("ALTER TABLE tickets ADD COLUMN autorise INTEGER DEFAULT 0")

    # Paiements
    cr.execute("""
    CREATE TABLE IF NOT EXISTS paiements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        montant REAL,
        date_paiement TEXT,
        FOREIGN KEY(user_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
    )
    """)

    # Tarifs
    cr.execute("""
    CREATE TABLE IF NOT EXISTS tarifs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prix_par_heure REAL
    )
    """)

    # Initialisation places et tarifs
    cr.execute("SELECT COUNT(*) FROM places")
    if cr.fetchone()[0] == 0:
        for _ in range(24):
            cr.execute("INSERT INTO places(libre) VALUES (1)")

    cr.execute("SELECT COUNT(*) FROM tarifs")
    if cr.fetchone()[0] == 0:
        cr.execute("INSERT INTO tarifs(prix_par_heure) VALUES (3)")  # Nouveau tarif: 3 DH/h
    else:
        cr.execute("UPDATE tarifs SET prix_par_heure = 3")

    db.commit()
    db.close()


if __name__ == "__main__":
    init_db()
