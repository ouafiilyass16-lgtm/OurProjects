import sqlite3

class Utilisateur:
    def __init__(self, nom, email, password, role="client"):
        self.nom = nom
        self.email = email
        self.password = password
        self.role = role

    def enregistrer(self):
        db = sqlite3.connect("instance/parking.db")
        cr = db.cursor()
        cr.execute(
            "INSERT INTO utilisateurs (nom,email,password,role) VALUES (?,?,?,?)",
            (self.nom, self.email, self.password, self.role)
        )
        db.commit()
        db.close()

    @staticmethod
    def verifier_connexion(email, password):
        db = sqlite3.connect("instance/parking.db")
        cr = db.cursor()
        cr.execute(
            "SELECT * FROM utilisateurs WHERE email=? AND password=?",
            (email, password)
        )
        user = cr.fetchone()
        db.close()
        return user
