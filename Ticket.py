# Ticket.py
import sqlite3
from datetime import datetime

class Ticket:
    def __init__(self, user_id, vehicule_id, place_id):
        self.user_id = user_id
        self.vehicule_id = vehicule_id
        self.place_id = place_id
        self.date_entree = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.date_sortie = None
        self.montant = 0

    def creer(self):
        db = sqlite3.connect("instance/parking.db")
        cr = db.cursor()
        cr.execute("""
        INSERT INTO tickets (user_id, vehicule_id, place_id, date_entree)
        VALUES (?,?,?,?)
        """, (self.user_id, self.vehicule_id, self.place_id, self.date_entree))
        db.commit()
        db.close()

    @staticmethod
    def calculer_montant(ticket_id):
        db = sqlite3.connect("instance/parking.db")
        cr = db.cursor()
        cr.execute("SELECT date_entree FROM tickets WHERE id=?", (ticket_id,))
        entree = cr.fetchone()[0]
        entree_dt = datetime.strptime(entree, "%Y-%m-%d %H:%M")
        sortie_dt = datetime.now()
        duree = (sortie_dt - entree_dt).total_seconds() / 3600  # heures
        cr.execute("SELECT prix_par_heure FROM tarifs LIMIT 1")
        prix = cr.fetchone()[0]
        montant = round(duree * prix, 2)
        db.close()
        return montant
