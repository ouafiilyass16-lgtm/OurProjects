import sqlite3

class Place:
    @staticmethod
    def places_libres():
        db = sqlite3.connect("instance/parking.db")
        cr = db.cursor()
        cr.execute("SELECT * FROM places WHERE libre=1")
        res = cr.fetchall()
        db.close()
        return res

    @staticmethod
    def occuper(place_id):
        db = sqlite3.connect("instance/parking.db")
        cr = db.cursor()
        cr.execute("UPDATE places SET libre=0 WHERE id=?", (place_id,))
        db.commit()
        db.close()

    @staticmethod
    def liberer(place_id):
        db = sqlite3.connect("instance/parking.db")
        cr = db.cursor()
        cr.execute("UPDATE places SET libre=1 WHERE id=?", (place_id,))
        db.commit()
        db.close()
