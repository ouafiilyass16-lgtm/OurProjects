from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from datetime import datetime
from database import init_db, DB_PATH
from GestionParking import GestionParking
import sqlite3
from Utilisateur import Utilisateur
from Place import Place
from Vehicule import Vehicule
from Ticket import Ticket
from Paiement import Paiement
import calendar
import os
import json

app = Flask(__name__)
app.secret_key = "secret"
app.config['TEMPLATES_AUTO_RELOAD'] = True

# S'assurer que la base de données est initialisée
init_db()


# ---------------- Landing Page ----------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------- Login ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = Utilisateur.verifier_connexion(email, password)

        if user:
            session["user_id"] = user[0]
            role_lower = user[4].lower()
            session["role"] = role_lower
            session["user_name"] = user[1]

            if role_lower == "admin":
                return redirect(url_for("admin_dashboard"))
            elif role_lower == "gardien":
                return redirect(url_for("gardien_dashboard"))
            else:
                return redirect(url_for("client_dashboard"))

        flash("❌ Email ou mot de passe incorrect", "error")
    return render_template("login.html")


# ---------------- Inscription ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role", "client")

        if role.lower() not in ["client", "gardien", "admin"]:
            role = "client"

        user = Utilisateur(nom, email, password, role)
        try:
            user.enregistrer()
            flash("Compte créé avec succès ! Connectez-vous.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash("❌ Email déjà utilisé ou erreur lors de l'inscription", "error")
    return render_template("register.html")


# ---------------- Client Dashboard ----------------
@app.route("/client")
def client_dashboard():
    if session.get("role") != "client":
        return redirect(url_for("login"))

    user_id = session["user_id"]

    with sqlite3.connect(DB_PATH) as db:
        cr = db.cursor()
        cr.execute("""
            SELECT p.id, p.libre, v.matricule, v.marque
            FROM places p
            LEFT JOIN tickets t ON p.id = t.place_id AND t.date_sortie IS NULL
            LEFT JOIN vehicules v ON t.vehicule_id = v.id
            ORDER BY p.id ASC
        """)
        places_data = cr.fetchall()

        cr.execute("""
            SELECT t.id, t.place_id, t.date_entree, t.autorise, v.matricule
            FROM tickets t
            JOIN vehicules v ON t.vehicule_id = v.id
            WHERE t.user_id = ? AND t.date_sortie IS NULL
        """, (user_id,))
        current_ticket = cr.fetchone()

        cr.execute("""
            SELECT date_entree, date_sortie, montant
            FROM tickets
            WHERE user_id = ? AND date_sortie IS NOT NULL
            ORDER BY date_sortie DESC LIMIT 10
        """, (user_id,))
        history = cr.fetchall()

    duration_str = "0h 0m"
    if current_ticket:
        date_entree = datetime.strptime(current_ticket[2], "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - date_entree
        hours = int(diff.total_seconds() // 3600)
        minutes = int((diff.total_seconds() % 3600) // 60)
        duration_str = f"{hours}h {minutes}m"

    mid = len(places_data) // 2
    row1 = places_data[:mid]
    row2 = places_data[mid:]

    return render_template("dashboard_client.html",
                           row1=row1, row2=row2,
                           current_ticket=current_ticket,
                           duration=duration_str,
                           history=history)


# ---------------- Gardien Dashboard ----------------
@app.route("/gardien")
def gardien_dashboard():
    if session.get("role") != "gardien":
        return redirect(url_for("login"))

    with sqlite3.connect(DB_PATH) as db:
        cr = db.cursor()
        cr.execute("""
            SELECT t.id, u.nom, v.matricule, p.id, t.date_entree
            FROM tickets t
            JOIN utilisateurs u ON t.user_id=u.id
            JOIN vehicules v ON t.vehicule_id=v.id
            JOIN places p ON t.place_id=p.id
            WHERE t.date_sortie IS NULL AND t.autorise = 0
        """)
        pending_exits = cr.fetchall()

        cr.execute("SELECT COUNT(*) FROM tickets WHERE date_sortie IS NULL")
        nb_parked = cr.fetchone()[0]

        today = datetime.now().strftime("%Y-%m-%d")
        cr.execute("SELECT COUNT(*) FROM tickets WHERE date_entree LIKE ?", (today + "%",))
        nb_entries_today = cr.fetchone()[0]

        cr.execute("SELECT COUNT(*) FROM tickets WHERE date_sortie LIKE ?", (today + "%",))
        nb_exits_today = cr.fetchone()[0]

        cr.execute("SELECT id, libre FROM places ORDER BY id ASC")
        places = cr.fetchall()

    return render_template("dashboard_gardien.html",
                           pending_exits=pending_exits,
                           nb_parked=nb_parked,
                           nb_entries_today=nb_entries_today,
                           nb_exits_today=nb_exits_today,
                           places=places)


@app.route("/autoriser_sortie", methods=["POST"])
def autoriser_sortie():
    if session.get("role") != "gardien":
        return redirect(url_for("login"))

    ticket_id = request.form.get("ticket_id")
    with sqlite3.connect(DB_PATH) as db:
        cr = db.cursor()
        cr.execute("UPDATE tickets SET autorise=1 WHERE id=?", (ticket_id,))
        db.commit()

    flash("Sortie autorisée avec succès", "success")
    return redirect(url_for("gardien_dashboard"))


# ---------------- Admin Dashboard ----------------
@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    with sqlite3.connect(DB_PATH) as db:
        cr = db.cursor()

        # 1. KPIs de base
        cr.execute("SELECT COUNT(*) FROM utilisateurs WHERE LOWER(role)='client'")
        nb_users = cr.fetchone()[0]

        cr.execute("SELECT COUNT(*) FROM vehicules")
        nb_vehicules = cr.fetchone()[0]

        cr.execute("SELECT SUM(montant) FROM tickets WHERE date_sortie IS NOT NULL")
        res = cr.fetchone()[0]
        chiffre_total = res if res else 0

        cr.execute("SELECT COUNT(*) FROM places")
        places_totales = cr.fetchone()[0]

        cr.execute("SELECT COUNT(*) FROM places WHERE libre=1")
        places_libres = cr.fetchone()[0]

        cr.execute("SELECT COUNT(*) FROM places WHERE libre=0")
        places_occupees = cr.fetchone()[0]

        cr.execute("SELECT COUNT(*) FROM tickets WHERE date_sortie IS NULL AND autorise=0")
        sorties_en_attente = cr.fetchone()[0]

        # 2. Revenus (Jour, Mois, Année)
        today = datetime.now().strftime("%Y-%m-%d")
        this_month = datetime.now().strftime("%Y-%m")
        this_year = datetime.now().strftime("%Y")

        cr.execute("SELECT SUM(montant) FROM tickets WHERE date_sortie LIKE ?", (today + "%",))
        res_j = cr.fetchone()[0]
        chiffre_journalier = res_j if res_j else 0

        cr.execute("SELECT SUM(montant) FROM tickets WHERE date_sortie LIKE ?", (this_month + "%",))
        res_m = cr.fetchone()[0]
        chiffre_mensuel = res_m if res_m else 0

        cr.execute("SELECT SUM(montant) FROM tickets WHERE date_sortie LIKE ?", (this_year + "%",))
        res_y = cr.fetchone()[0]
        chiffre_annuel = res_y if res_y else 0

        cr.execute("SELECT COUNT(*) FROM tickets WHERE date_sortie LIKE ?", (today + "%",))
        tickets_clotures_today = cr.fetchone()[0]

        # 3. Données pour les graphiques
        cr.execute("""
            SELECT strftime('%H', date_entree) as heure, COUNT(*) 
            FROM tickets WHERE date_entree LIKE ? 
            GROUP BY heure
        """, (today + "%",))
        entrees_par_heure = dict(cr.fetchall())

        cr.execute("""
            SELECT strftime('%H', date_sortie) as heure, COUNT(*) 
            FROM tickets WHERE date_sortie LIKE ? 
            GROUP BY heure
        """, (today + "%",))
        sorties_par_heure = dict(cr.fetchall())

        cr.execute("""
            SELECT strftime('%Y-%m-%d', date_sortie) as jour, SUM(montant)
            FROM tickets WHERE date_sortie IS NOT NULL
            GROUP BY jour ORDER BY jour DESC LIMIT 7
        """)
        revenus_7j = cr.fetchall()

        # 4. Tables de données
        cr.execute("""
            SELECT t.date_entree, t.date_sortie, t.montant, u.nom, v.matricule
            FROM tickets t
            JOIN utilisateurs u ON t.user_id = u.id
            JOIN vehicules v ON t.vehicule_id = v.id
            WHERE t.date_sortie IS NOT NULL
            ORDER BY t.date_sortie DESC LIMIT 10
        """)
        dernieres_sorties = cr.fetchall()

        cr.execute("SELECT id, nom, email FROM utilisateurs WHERE LOWER(role)='client'")
        utilisateurs_rows = cr.fetchall()
        utilisateurs = [{"id": r[0], "nom": r[1], "email": r[2]} for r in utilisateurs_rows]

        cr.execute("""
            SELECT v.matricule, v.marque, v.couleur, u.nom
            FROM vehicules v
            JOIN utilisateurs u ON v.user_id = u.id
        """)
        vehicules_rows = cr.fetchall()
        vehicules = [{"matricule": r[0], "marque": r[1], "couleur": r[2], "user": r[3]} for r in vehicules_rows]

    return render_template(
        "dashboard_admin.html",
        nb_users=nb_users,
        nb_vehicules=nb_vehicules,
        chiffre_total=chiffre_total,
        chiffre_journalier=chiffre_journalier,
        chiffre_mensuel=chiffre_mensuel,
        chiffre_annuel=chiffre_annuel,
        places_totales=places_totales,
        places_libres=places_libres,
        places_occupees=places_occupees,
        sorties_en_attente=sorties_en_attente,
        tickets_clotures_today=tickets_clotures_today,
        entrees_par_heure=json.dumps(entrees_par_heure),
        sorties_par_heure=json.dumps(sorties_par_heure),
        revenus_7j=json.dumps(dict(revenus_7j)),
        dernieres_sorties=dernieres_sorties,
        utilisateurs=utilisateurs,
        vehicules=vehicules,
        now=datetime.now()
    )


@app.route("/choisir_place", methods=["POST"])
def choisir_place():
    if session.get("role") != "client":
        return redirect(url_for("login"))

    user_id = session["user_id"]
    place_id = request.form.get("place_id")
    matricule = request.form.get("matricule")
    marque = request.form.get("marque")
    couleur = request.form.get("couleur")

    with sqlite3.connect(DB_PATH) as db:
        cr = db.cursor()
        cr.execute("SELECT COUNT(*) FROM tickets WHERE user_id=? AND date_sortie IS NULL", (user_id,))
        if cr.fetchone()[0] > 0:
            flash("❌ Vous avez déjà une réservation en cours !", "error")
            return redirect(url_for("client_dashboard"))

        cr.execute("INSERT INTO vehicules (matricule, marque, couleur, user_id) VALUES (?,?,?,?)",
                   (matricule, marque, couleur, user_id))
        vehicule_id = cr.lastrowid

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cr.execute("INSERT INTO tickets (user_id, vehicule_id, place_id, date_entree, autorise) VALUES (?,?,?,?,0)",
                   (user_id, vehicule_id, place_id, now))

        cr.execute("UPDATE places SET libre=0 WHERE id=?", (place_id,))
        db.commit()

    flash("Place réservée avec succès !", "success")
    return redirect(url_for("client_dashboard"))


@app.route("/cloturer_ticket", methods=["POST"])
def cloturer_ticket():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    ticket_id = request.form.get("ticket_id")

    with sqlite3.connect(DB_PATH) as db:
        cr = db.cursor()
        cr.execute("""
            SELECT t.date_entree, t.place_id, t.user_id, t.vehicule_id, t.autorise, u.nom, v.matricule
            FROM tickets t
            JOIN utilisateurs u ON t.user_id = u.id
            JOIN vehicules v ON t.vehicule_id = v.id
            WHERE t.id=?
        """, (ticket_id,))
        ticket_info = cr.fetchone()

        if not ticket_info or ticket_info[4] == 0:
            flash("Sortie non autorisée ou ticket introuvable", "error")
            return redirect(url_for("client_dashboard"))

        date_entree_str, place_id, user_id, vehicule_id, _, nom_client, matricule = ticket_info
        date_entree = datetime.strptime(date_entree_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        diff = now - date_entree
        duree_heures = diff.total_seconds() / 3600

        montant = round(max(1, duree_heures) * 3, 2)

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

        ticket_res = {
            "id": ticket_id, "nom": nom_client, "matricule": matricule,
            "place_id": place_id, "date_entree": date_entree_str,
            "date_sortie": now.strftime("%Y-%m-%d %H:%M:%S"),
            "duree_heures": round(duree_heures, 2), "montant": montant
        }
        return render_template("recu.html", ticket=ticket_res)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(port=3000, debug=True)
