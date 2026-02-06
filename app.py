from flask import Flask, render_template, request, redirect, session
from datetime import datetime
from database import init_db, DB_PATH
from GestionParking import GestionParking
import sqlite3
from Utilisateur import Utilisateur
from Place import Place
from Vehicule import Vehicule
from Ticket import Ticket
from Paiement import Paiement
from datetime import datetime
import calendar


app = Flask(__name__)
app.secret_key = "secret"
app.config['TEMPLATES_AUTO_RELOAD'] = True
init_db()

# ---------------- Landing Page ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- Login ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Utilisateur.verifier_connexion(request.form["email"], request.form["password"])
        if user:
            print("Utilisateur trouvé:", user)
            session["user_id"] = user[0]
            role_lower = user[4].lower()
            session["role"] = role_lower

            if role_lower == "admin":
                return redirect("/admin")
            elif role_lower == "gardien":
                return redirect("/gardien")
            else:
                return redirect("/client")
        return "❌ Email ou mot de passe incorrect"
    return render_template("login.html")

# ---------------- Inscription ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form.get("role")
        if role not in ["client"]:
            role = "client"
        user = Utilisateur(nom, email, password, role)
        try:
            user.enregistrer()
            return redirect("/login")
        except:
            return "❌ Email déjà utilisé"
    return render_template("register.html")

# ---------------- Client Dashboard ----------------
@app.route("/client")
def client_dashboard():
    if session.get("role") != "client":
        return redirect("/")
    places = Place.places_libres()
    return render_template("dashboard_client.html", places=places)

# ---------------- Gardien Dashboard ----------------
@app.route("/gardien", methods=["GET", "POST"])
def gardien_dashboard():
    if session.get("role") != "gardien":
        return redirect("/")

    # Récupérer tous les tickets en cours
    with sqlite3.connect(DB_PATH) as db:
        cr = db.cursor()
        cr.execute("""
            SELECT t.id, u.nom, v.matricule, p.id, t.date_entree
            FROM tickets t
            JOIN utilisateurs u ON t.user_id=u.id
            JOIN vehicules v ON t.vehicule_id=v.id
            JOIN places p ON t.place_id=p.id
            WHERE t.date_sortie IS NULL
        """)
        tickets = cr.fetchall()

    return render_template("dashboard_gardien.html", tickets=tickets)


@app.route("/valider_ticket", methods=["POST"])
def valider_ticket():
    if session.get("role") != "gardien":
        return redirect("/")

    ticket_id = request.form["ticket_id"]

    with sqlite3.connect(DB_PATH) as db:
        cr = db.cursor()
        # Autoriser la sortie
        cr.execute("UPDATE tickets SET autorise=1 WHERE id=?", (ticket_id,))
        db.commit()

    return redirect("/gardien")


# ---------------- Admin Dashboard ----------------
@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/")

    # Statistiques globales
    nb_users, nb_vehicules, chiffre_total = GestionParking.get_stats_admin()

    # Chiffre journalier (aujourd'hui)
    chiffre_journalier = GestionParking.get_chiffre_journalier()

    # Chiffre mensuel (ce mois)
    chiffre_mensuel = GestionParking.get_chiffre_mensuel()

    # Liste des utilisateurs (clients)
    utilisateurs = GestionParking.get_users()  # liste de dicts avec id, nom, email

    # Liste des véhicules
    vehicules = GestionParking.get_vehicules()  # liste de dicts avec id, matricule, marque, couleur, user

    return render_template(
        "dashboard_admin.html",
        nb_users=nb_users,
        nb_vehicules=nb_vehicules,
        chiffre_total=chiffre_total,
        chiffre_journalier=chiffre_journalier,
        chiffre_mensuel=chiffre_mensuel,
        utilisateurs=utilisateurs,
        vehicules=vehicules
    )



@app.route("/choisir_place", methods=["POST"])
def choisir_place():
    if session.get("role") != "client":
        return redirect("/")

    user_id = session["user_id"]
    place_id = request.form["place_id"]
    matricule = request.form["matricule"]
    marque = request.form["marque"]
    couleur = request.form["couleur"]

    with sqlite3.connect("instance/parking.db") as db:
        cr = db.cursor()

        # Vérifier si le client a déjà un véhicule en cours
        cr.execute("""
            SELECT COUNT(*) FROM tickets
            WHERE user_id=? AND date_sortie IS NULL
        """, (user_id,))
        actif = cr.fetchone()[0]

        if actif > 0:
            return "❌ Vous avez déjà une réservation en cours !"

        # Ajouter véhicule
        cr.execute(
            "INSERT INTO vehicules (matricule, marque, couleur, user_id) VALUES (?,?,?,?)",
            (matricule, marque, couleur, user_id)
        )
        # Récupérer l'id du véhicule ajouté
        cr.execute("SELECT id FROM vehicules WHERE matricule=?", (matricule,))
        vehicule_id = cr.fetchone()[0]

        # Créer ticket
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cr.execute(
            """INSERT INTO tickets (user_id, vehicule_id, place_id, date_entree, date_sortie, montant)
               VALUES (?,?,?,?,?,?)""",
            (user_id, vehicule_id, place_id, now, None, None)
        )

        # Occuper la place
        cr.execute("UPDATE places SET libre=0 WHERE id=?", (place_id,))

        db.commit()

    return redirect("/client")


@app.route("/sortir", methods=["GET", "POST"])
def sortie_voiture():
    if session.get("role") not in ["admin", "gardien", "client"]:
        return redirect("/")

    with sqlite3.connect(DB_PATH) as db:  # connexion sécurisée
        cr = db.cursor()

        if request.method == "POST":
            ticket_id = request.form["ticket_id"]

            # Récupérer le ticket
            cr.execute("SELECT date_entree, place_id, user_id, vehicule_id FROM tickets WHERE id=?", (ticket_id,))
            ticket_info = cr.fetchone()
            if not ticket_info:
                return "❌ Ticket introuvable"

            date_entree_str, place_id, user_id, vehicule_id = ticket_info
            date_entree = datetime.strptime(date_entree_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            duree_heures = (now - date_entree).total_seconds() / 3600  # durée en heures

            # Récupérer le tarif
            cr.execute("SELECT prix_par_heure FROM tarifs LIMIT 1")
            tarif = cr.fetchone()[0]

            montant = round(duree_heures * tarif, 2)

            # Mettre à jour ticket + libérer place + ajouter paiement
            cr.execute(
                "UPDATE tickets SET date_sortie=?, montant=? WHERE id=?",
                (now.strftime("%Y-%m-%d %H:%M:%S"), montant, ticket_id)
            )
            cr.execute("UPDATE places SET libre=1 WHERE id=?", (place_id,))
            cr.execute(
                "INSERT INTO paiements(user_id, montant, date_paiement) VALUES (?,?,?)",
                (user_id, montant, now.strftime("%Y-%m-%d %H:%M:%S"))
            )
            db.commit()

            # Préparer les infos pour le reçu **avant de fermer la base**
            cr.execute("SELECT nom FROM utilisateurs WHERE id=?", (user_id,))
            nom_client = cr.fetchone()[0]

            cr.execute("SELECT matricule FROM vehicules WHERE id=?", (vehicule_id,))
            matricule = cr.fetchone()[0]

            ticket = {
                "id": ticket_id,
                "nom": nom_client,
                "matricule": matricule,
                "place_id": place_id,
                "date_entree": date_entree_str,
                "date_sortie": now.strftime("%Y-%m-%d %H:%M:%S"),
                "duree_heures": round(duree_heures, 2),
                "montant": montant
            }

            return render_template("recu.html", ticket=ticket)

        # GET → afficher les tickets en cours
        # GET → afficher les tickets en cours
        if session.get("role") == "Client":
            user_id = session["user_id"]
            cr.execute("""
                SELECT t.id, u.nom, v.matricule, p.id, t.date_entree, t.autorise
                FROM tickets t
                JOIN utilisateurs u ON t.user_id=u.id
                JOIN vehicules v ON t.vehicule_id=v.id
                JOIN places p ON t.place_id=p.id
                WHERE t.date_sortie IS NULL AND t.user_id=?
            """, (user_id,))
        else:
            # Pour Admin ou Gardien
            cr.execute("""
                SELECT t.id, u.nom, v.matricule, p.id, t.date_entree, t.autorise
                FROM tickets t
                JOIN utilisateurs u ON t.user_id=u.id
                JOIN vehicules v ON t.vehicule_id=v.id
                JOIN places p ON t.place_id=p.id
                WHERE t.date_sortie IS NULL
            """)
        tickets = cr.fetchall()


    return render_template("sortir.html", tickets=tickets)


# ---------------- Logout ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(port = 3000)