import sqlite3
from datetime import datetime

class Paiement:
    def __init__(self, user_id, montant):
        self.user_id = user_id
        self.montant = montant
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M")

    def payer(self):
        db = sqlite3.connect("instance/parking.db")
        cr = db.cursor()
        cr.execute(
            "INSERT INTO paiements (user_id, montant, date_paiement) VALUES (?,?,?)",
            (self.user_id, self.montant, self.date)
        )
        db.commit()
        db.close()
