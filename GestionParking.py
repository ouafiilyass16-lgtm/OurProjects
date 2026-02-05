import sqlite3
from database import DB_PATH
from datetime import datetime

class GestionParking:

    @staticmethod
    def get_stats_admin():
        with sqlite3.connect(DB_PATH) as db:
            cr = db.cursor()
            cr.execute("SELECT COUNT(*) FROM utilisateurs WHERE role='Client'")
            nb_users = cr.fetchone()[0]

            cr.execute("SELECT COUNT(*) FROM vehicules")
            nb_vehicules = cr.fetchone()[0]

            cr.execute("SELECT SUM(montant) FROM paiements")
            res = cr.fetchone()[0]
            chiffre = res if res else 0

        return nb_users, nb_vehicules, chiffre

    @staticmethod
    def get_chiffre_journalier():
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(DB_PATH) as db:
            cr = db.cursor()
            cr.execute("SELECT SUM(montant) FROM paiements WHERE date_paiement LIKE ?", (today + "%",))
            res = cr.fetchone()[0]
            return res if res else 0

    @staticmethod
    def get_chiffre_mensuel():
        month = datetime.now().strftime("%Y-%m")
        with sqlite3.connect(DB_PATH) as db:
            cr = db.cursor()
            cr.execute("SELECT SUM(montant) FROM paiements WHERE date_paiement LIKE ?", (month + "%",))
            res = cr.fetchone()[0]
            return res if res else 0

    @staticmethod
    def get_users():
        with sqlite3.connect(DB_PATH) as db:
            cr = db.cursor()
            cr.execute("SELECT id, nom, email FROM utilisateurs WHERE role='Client'")
            rows = cr.fetchall()
            return [{"id": r[0], "nom": r[1], "email": r[2]} for r in rows]

    @staticmethod
    def get_vehicules():
        with sqlite3.connect(DB_PATH) as db:
            cr = db.cursor()
            cr.execute("""
                SELECT v.id, v.matricule, v.marque, v.couleur, u.nom
                FROM vehicules v
                JOIN utilisateurs u ON v.user_id = u.id
            """)
            rows = cr.fetchall()
            return [{"id": r[0], "matricule": r[1], "marque": r[2], "couleur": r[3], "user": r[4]} for r in rows]
