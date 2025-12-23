import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# ============================================================================
# n8n (TEST) – URLs issues de ta feuille Google Sheets http://localhost:5678/webhook-test/annuler_rdv
# ============================================================================
N8N_BASE = "http://localhost:5678"
WEBHOOKS = {
    # Patient
    "login_patient":       f"{N8N_BASE}/webhook-test/cnxpatient",
    "register_patient":    f"{N8N_BASE}/webhook-test/inscription_patients",
    "form_patient_rdv":    f"{N8N_BASE}/webhook-test/form_patient_rdv",
    "cancel_rdv":          f"{N8N_BASE}/webhook-test/annuler_rdv",

    # Médecin
    "login_medecin":       f"{N8N_BASE}/webhook-test/cnxmedecin",
    "register_medecin":    f"{N8N_BASE}/webhook-test/inscription_medecin",

    # Secrétaire / Staff (espaces dans templates/admin/*)
    "login_secretaire":    f"{N8N_BASE}/webhook-test/cnxsecretaires",
    "register_secretaire": f"{N8N_BASE}/webhook-test/inscription_Secretaire",

    # Staff (optionnel)
    "staff_creneaux_confirmes": f"{N8N_BASE}/webhook-test/staff-creneaux-confirmes",
}
REQUEST_TIMEOUT = 20  # secondes


def safe_json(resp):
    """Parse JSON sans casser si non-JSON."""
    try:
        return resp.json()
    except Exception:
        return {}


# Conventions confirmées 
# - Inscription => { "ok": true, ... }
# - Connexion   => { "status": "connexion réussie" }
def success_register(data: dict) -> bool:
    return data.get("ok") is True

def success_login(data: dict) -> bool:
    return (data.get("status") or "").strip().lower() == "connexion réussie"


# ============================================================================
# ACCUEIL
# ============================================================================
@app.route("/")
def index():
    return render_template("index.html")


# ============================================================================
# PATIENT (templates à la racine)
# ============================================================================
@app.route("/patient")
def patient_space():
    return render_template("patienthome.html")


# --- Connexion patient ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()
        try:
            resp = requests.post(
                WEBHOOKS["login_patient"],
                json={"email": email, "password": password},
                timeout=REQUEST_TIMEOUT,
            )
            print("n8n login patient:", resp.status_code, resp.text)
            data = safe_json(resp)
            if resp.ok and success_login(data):
                session["user_email"] = email
                session["role"] = "patient"
                flash("Connexion réussie.", "success")
                return redirect(url_for("patient_space"))
            elif resp.ok:
                flash(data.get("message", "Email ou mot de passe incorrect."), "error")
            else:
                flash("Erreur de connexion au serveur n8n.", "error")
        except Exception as e:
            print("Erreur n8n (login patient):", e)
            flash("Erreur de connexion au serveur n8n.", "error")
        return redirect(url_for("login"))
    return render_template("login.html")


# --- Inscription patient ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = (request.form.get("nom") or "").strip()
        prenom = (request.form.get("prenom") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()
        try:
            resp = requests.post(
                WEBHOOKS["register_patient"],
                json={"nom": nom, "prenom": prenom, "email": email, "password": password},
                timeout=REQUEST_TIMEOUT,
            )
            print("n8n register patient:", resp.status_code, resp.text)
            data = safe_json(resp)
            if resp.ok and success_register(data):
                flash(data.get("message", "Inscription réussie."), "success")
                if data.get("id_patient"):
                    session["id_patient"] = data["id_patient"]
                session["user_email"] = email
                session["role"] = "patient"
                return redirect(url_for("patient_space"))
            elif resp.ok:
                flash(data.get("message", "Inscription impossible."), "error")
            else:
                flash("Erreur lors de l'inscription.", "error")
        except Exception as e:
            print("Erreur n8n (register patient):", e)
            flash("Erreur de connexion au serveur d'inscription.", "error")
        return redirect(url_for("register"))
    return render_template("register.html")


# --- Formulaire RDV patient ---
@app.route("/patientform", methods=["GET", "POST"])
def patient_form():
    if request.method == "POST":
        form_data = {
            "nom": request.form.get("nom"),
            "prenom": request.form.get("prenom"),
            "cin": request.form.get("cin"),
            "age": request.form.get("age"),
            "email": request.form.get("email"),
            "assurance": request.form.get("assurance"),
            "besoin": request.form.get("besoin"),
        }
        try:
            resp = requests.post(
                WEBHOOKS["form_patient_rdv"],
                json=form_data,
                timeout=REQUEST_TIMEOUT,
            )
            print("n8n form rdv:", resp.status_code, resp.text)

            # Lecture JSON tolérante + extraction du message
            data = safe_json(resp)
            msg = None
            if isinstance(data, dict):
                msg = data.get("message") or data.get("messsage") or data.get("msg")
            elif isinstance(data, list) and data:
                first = data[0] if isinstance(data[0], dict) else {}
                msg = first.get("message") or first.get("messsage") or first.get("msg")

            if resp.ok:
                flash(msg or "Rendez-vous enregistré avec succès !", "success")
            else:
                flash(msg or "Une erreur est survenue, veuillez réessayer plus tard.", "error")

        except Exception as e:
            print("Erreur n8n (form RDV):", e)
            flash("Une erreur est survenue, veuillez réessayer plus tard.", "error")

    return render_template("patientform.html")


# --- Dashboard patient (liste maquette + annulation réelle via n8n) ---
RENDEZVOUS = [
    {"id_rdv": "10543","id_patient": "P243","date": "15/08/2025","heure": "10:00","medecin": "Dr. Benali","service": "Médecine Générale","specialite": "Cardiologie","consultation": "Oui","statut": "Confirmé"},
    {"id_rdv": "10544","id_patient": "P243","date": "20/08/2025","heure": "14:30","medecin": "Dr. El Alaoui","service": "Dermatologie","specialite": "Dermatologie","consultation": "Non","statut": "En attente"},
    {"id_rdv": "10545","id_patient": "P243","date": "01/09/2025","heure": "09:00","medecin": "Dr. Khadija","service": "Pédiatrie","specialite": "Pédiatrie","consultation": "Non","statut": "Annulé"},
]

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # Annulation via n8n
    if request.method == "POST":
        id_rdv = (request.form.get("id_rdv") or "").strip()

        try:
            print("➡️ N8N_BASE:", N8N_BASE)
            print("➡️ URL cancel (config):", WEBHOOKS["cancel_rdv"])

            resp = requests.post(
                WEBHOOKS["cancel_rdv"],
                json={"id_rdv": id_rdv},
                timeout=REQUEST_TIMEOUT,
            )

            print("n8n cancel rdv -> called:", resp.request.url)
            print("n8n cancel rdv -> status:", resp.status_code, "| body:", resp.text)

            data = safe_json(resp)

            if resp.ok:
                flash(data.get("message", "Rendez-vous annulé avec succès."), "success")
            else:
                flash(data.get("message", "Erreur lors de l'annulation du rendez-vous."), "error")

        except Exception as e:
            print("Erreur n8n (annulation):", e)
            flash("Erreur de connexion au serveur n8n.", "error")

    return render_template("dashboardpatient.html", rendezvous=RENDEZVOUS)



# ============================================================================
# MEDECIN (templates dans templates/medecin)
# ============================================================================
@app.route("/medecinhome", methods=["GET"])
def medecin_home():
    return render_template("medecin/medecinhome.html")



@app.route("/loginmedecin", methods=["GET", "POST"])
def login_medecin():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()
        try:
            resp = requests.post(
                WEBHOOKS["login_medecin"],
                json={"email": email, "password": password},
                timeout=REQUEST_TIMEOUT,
            )
            print("n8n login medecin:", resp.status_code, resp.text)
            data = safe_json(resp)
            if resp.ok and success_login(data):
                session["user_email"] = email
                session["role"] = "medecin"
                flash("Connexion réussie.", "success")
                return redirect(url_for("medecin_home"))
            elif resp.ok:
                flash(data.get("message", "Email ou mot de passe incorrect."), "error")
            else:
                flash("Erreur de connexion au serveur n8n.", "error")
        except Exception as e:
            print("Erreur n8n (login medecin):", e)
            flash("Erreur de connexion au serveur n8n.", "error")
        return redirect(url_for("login_medecin"))
    return render_template("medecin/loginmedecin.html")


@app.route("/registermedecin", methods=["GET", "POST"])
def register_medecin():
    if request.method == "POST":
        nom = (request.form.get("nom") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()
        try:
            resp = requests.post(
                WEBHOOKS["register_medecin"],
                json={"nom": nom, "email": email, "password": password},
                timeout=REQUEST_TIMEOUT,
            )
            print("n8n register medecin:", resp.status_code, resp.text)
            data = safe_json(resp)
            if resp.ok and success_register(data):
                flash(data.get("message", "Inscription réussie."), "success")
                session["user_email"] = email
                session["role"] = "medecin"
                return redirect(url_for("medecin_home"))
            elif resp.ok:
                flash(data.get("message", "Inscription impossible."), "error")
            else:
                flash("Erreur lors de l'inscription.", "error")
        except Exception as e:
            print("Erreur n8n (register medecin):", e)
            flash("Erreur de connexion au serveur d'inscription.", "error")
        return redirect(url_for("register_medecin"))
    return render_template("medecin/registermed.html")

@app.route("/disponibilites", methods=["GET"])
def disponibilites():
    return render_template("medecin/disponibilites.html")

@app.route("/dossierpatient", methods=["GET"])
def dossier_patient():
    return render_template("medecin/dossierpatient.html")

# ============================================================================
# SECRÉTAIRE / ADMIN  (utilise templates/admin/*)
# ============================================================================
@app.route("/adminhome", methods=["GET"])
def admin_home():
    return render_template("admin/adminhome.html")


@app.route("/loginadmin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()
        try:
            resp = requests.post(
                WEBHOOKS["login_secretaire"],
                json={"email": email, "password": password},
                timeout=REQUEST_TIMEOUT,
            )
            print("n8n login secretaire:", resp.status_code, resp.text)
            data = safe_json(resp)
            if resp.ok and success_login(data):
                session["user_email"] = email
                session["role"] = "secretaire"
                flash("Connexion réussie.", "success")
                return redirect(url_for("admin_home"))
            elif resp.ok:
                flash(data.get("message", "Email ou mot de passe incorrect."), "error")
            else:
                flash("Erreur de connexion au serveur n8n.", "error")
        except Exception as e:
            print("Erreur n8n (login secretaire):", e)
            flash("Erreur de connexion au serveur n8n.", "error")
        return redirect(url_for("login_admin"))
    return render_template("admin/loginadmin.html")


@app.route("/registeradmin", methods=["GET", "POST"])
def register_admin():
    if request.method == "POST":
        nom = (request.form.get("nom") or "").strip()
        prenom = (request.form.get("prenom") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()
        try:
            resp = requests.post(
                WEBHOOKS["register_secretaire"],
                json={"nom": nom, "prenom": prenom, "email": email, "password": password},
                timeout=REQUEST_TIMEOUT,
            )
            print("n8n register secretaire:", resp.status_code, resp.text)
            data = safe_json(resp)
            if resp.ok and success_register(data):
                flash(data.get("message", "Inscription réussie."), "success")
                session["user_email"] = email
                session["role"] = "secretaire"
                return redirect(url_for("admin_home"))
            elif resp.ok:
                flash(data.get("message", "Inscription impossible."), "error")
            else:
                flash("Erreur lors de l'inscription.", "error")
        except Exception as e:
            print("Erreur n8n (register secretaire):", e)
            flash("Erreur de connexion au serveur d'inscription.", "error")
        return redirect(url_for("register_admin"))
    return render_template("admin/registeradmin.html")


@app.route("/adminstats")
def admin_stats():
    return render_template("admin/adminstats.html")


@app.route("/admincomptes")
def admin_comptes():
    return render_template("admin/admincomptes.html")


# ============================================================================
# LOGOUT commun
# ============================================================================
@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("user_email", None)
    session.pop("role", None)
    session.pop("id_patient", None)
    flash("Vous êtes déconnecté(e).", "success")
    return redirect(url_for("login"))






# ============================================================================
# RUN
# ============================================================================
if __name__ == "__main__":
    app.run(debug=True)
