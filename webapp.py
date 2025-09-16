# webapp.py
import os
import sqlite3
from contextlib import closing
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
import requests


# Point UI at the existing IPL API (same host by default)
API_BASE = os.environ.get("API_BASE_URL", "http://127.0.0.1:5000")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret")
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        """)
        conn.commit()

class User(UserMixin):
    def __init__(self, id, email, password_hash):
        self.id = str(id)
        self.email = email
        self.password_hash = password_hash

def get_user_by_email(email):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, email, password_hash FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
    return User(*row) if row else None

def get_user_by_id(user_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, email, password_hash FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
    return User(*row) if row else None

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

@app.route("/")
def index():
    # If authenticated, land on dashboard; else show login
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# ---------- Auth ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm") or ""
        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("auth_register.html")
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("auth_register.html")
        if get_user_by_email(email):
            flash("User already exists.", "warning")
            return render_template("auth_register.html")
        pw_hash = generate_password_hash(password)
        with closing(sqlite3.connect(DB_PATH)) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, pw_hash))
            conn.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("auth_register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = get_user_by_email(email)
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials.", "danger")
            return render_template("auth_login.html")
        login_user(user, remember=False)
        flash("Logged in successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("auth_login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

# ---------- Dashboard (no JS; server calls API and renders) ----------
@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    # Preload teams for dropdowns
    try:
        resp = requests.get(f"{API_BASE}/api/teams", timeout=10)
        resp.raise_for_status()
        teams = sorted(resp.json().get("teams", []))
    except Exception as e:
        teams = []
        flash(f"Failed to load teams: {e}", "danger")
    return render_template("dashboard.html", teams=teams, h2h=None, team_record=None, player=None, player_type=None)

@app.route("/dashboard/h2h", methods=["POST"])
@login_required
def dashboard_h2h():
    team1 = request.form.get("team1") or ""
    team2 = request.form.get("team2") or ""
    teams = _load_teams_safe()
    h2h = None
    if team1 and team2:
        try:
            r = requests.get(f"{API_BASE}/api/teamvteam", params={"team1": team1, "team2": team2}, timeout=10)
            r.raise_for_status()
            h2h = r.json()
        except Exception as e:
            flash(f"Head-to-head error: {e}", "danger")
    return render_template("dashboard.html", teams=teams, h2h=h2h, team_record=None, player=None, player_type=None)

@app.route("/dashboard/team-record", methods=["POST"])
@login_required
def dashboard_team_record():
    team = request.form.get("team") or ""
    teams = _load_teams_safe()
    trec = None
    if team:
        try:
            r = requests.get(f"{API_BASE}/api/team-record", params={"team": team}, timeout=15)
            r.raise_for_status()
            trec = r.json()
        except Exception as e:
            flash(f"Team record error: {e}", "danger")
    return render_template("dashboard.html", teams=teams, h2h=None, team_record=trec, player=None, player_type=None)

@app.route("/dashboard/player", methods=["POST"])
@login_required
def dashboard_player():
    player_type = request.form.get("player_type") or "batting"
    name = request.form.get("name") or ""
    teams = _load_teams_safe()
    pdata = None
    if name:
        try:
            if player_type == "bowling":
                r = requests.get(f"{API_BASE}/api/bowling-record", params={"bowler": name}, timeout=15)
            else:
                r = requests.get(f"{API_BASE}/api/batting-record", params={"batsman": name}, timeout=15)
            r.raise_for_status()
            pdata = r.json()
        except Exception as e:
            flash(f"Player stats error: {e}", "danger")
    return render_template("dashboard.html", teams=teams, h2h=None, team_record=None, player=pdata, player_type=player_type)

def _load_teams_safe():
    try:
        resp = requests.get(f"{API_BASE}/api/teams", timeout=10)
        resp.raise_for_status()
        return sorted(resp.json().get("teams", []))
    except Exception:
        return []

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=7000)
