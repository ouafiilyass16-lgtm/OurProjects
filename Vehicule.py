import sqlite3

class Vehicule:
    def __init__(self, matricule, marque, couleur, user_id):
        self.matricule = matricule
        self.marque = marque
        self.couleur = couleur
        self.user_id = user_id

    def ajouter(self):
        """Ajoute un véhicule pour l'utilisateur à la base, sans verrouiller SQLite"""
        try:
            # with gère automatiquement db.close()
            with sqlite3.connect("instance/parking.db") as db:
                cr = db.cursor()
                cr.execute(
                    "INSERT INTO vehicules (matricule, marque, couleur, user_id) VALUES (?,?,?,?)",
                    (self.matricule, self.marque, self.couleur, self.user_id)
                )
                db.commit()  # facultatif, avec 'with', commit se fait à la fermeture
        except sqlite3.IntegrityError:
            print(f"❌ Le véhicule {self.matricule} existe déjà.")

    @staticmethod
    def vehicules_par_utilisateur(user_id):
        """Retourne tous les véhicules d'un utilisateur"""
        with sqlite3.connect("instance/parking.db") as db:
            cr = db.cursor()
            cr.execute("SELECT id, matricule, marque, couleur FROM vehicules WHERE user_id=?", (user_id,))
            result = cr.fetchall()
        return result
