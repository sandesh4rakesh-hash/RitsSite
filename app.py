"""
RITS Services — Professional company website
--------------------------------------------
Features:
  • Dual theme (dark / light) with toggle
  • Working language switcher (English / Hindi)
  • Portal with two logins:
        - Employee login via LDAP  (ldap3 if configured, demo fallback)
        - Customer login via Google account (OAuth if configured, demo fallback)
  • All menu pages: Home, About, Services, Industries, Portfolio,
    Careers, Blog, Contact (working contact form)

Run:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000
"""
import os
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify)
from flask import send_from_directory

from translations import TRANSLATIONS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "rits-dev-secret-change-me")

# ---------------------------------------------------------------------------
# Configuration (override with environment variables in production)
# ---------------------------------------------------------------------------
LDAP_SERVER   = os.environ.get("LDAP_SERVER", "")           # e.g. ldap://ldap.rits.local
LDAP_BASE_DN  = os.environ.get("LDAP_BASE_DN", "ou=users,dc=rits,dc=local")
LDAP_USER_ATTR = os.environ.get("LDAP_USER_ATTR", "uid")

GOOGLE_CLIENT_ID     = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

# Demo employee accounts used when no LDAP server is configured
DEMO_EMPLOYEES = {
    "admin":    {"password": "admin123",  "name": "Ravi Sharma",  "role": "Administrator"},
    "employee": {"password": "rits@2026", "name": "Priya Verma",  "role": "Software Engineer"},
}

# ---------------------------------------------------------------------------
# Optional Google OAuth (only active when client id/secret are provided)
# ---------------------------------------------------------------------------
oauth = None
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    try:
        from authlib.integrations.flask_client import OAuth
        oauth = OAuth(app)
        oauth.register(
            name="google",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )
    except ImportError:
        oauth = None


# ---------------------------------------------------------------------------
# i18n helpers
# ---------------------------------------------------------------------------
@app.context_processor
def inject_globals():
    lang = session.get("lang", "en")
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return {"t": t, "lang": lang, "now": datetime.now(),
            "user": session.get("user")}


@app.route("/set-language/<lang>")
def set_language(lang):
    if lang in TRANSLATIONS:
        session["lang"] = lang
    return redirect(request.referrer or url_for("home"))


def login_required(user_type=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = session.get("user")
            if not user:
                flash("Please log in to access the portal.", "warning")
                return redirect(url_for("portal"))
            if user_type and user.get("type") != user_type:
                flash("You do not have access to that portal.", "warning")
                return redirect(url_for("portal"))
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html", active="home")


@app.route("/about")
def about():
    return render_template("about.html", active="about")


@app.route("/services")
def services():
    return render_template("services.html", active="services")


@app.route("/industries")
def industries():
    return render_template("industries.html", active="industries")


@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html", active="portfolio")


@app.route("/careers")
def careers():
    return render_template("careers.html", active="careers")


@app.route("/blog")
def blog():
    return render_template("blog.html", active="blog")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not (name and email and message):
            flash("Please fill in all required fields.", "warning")
        else:
            # In production: send an email / store in a database here.
            with open("contact_messages.log", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now():%Y-%m-%d %H:%M}] {name} <{email}>: {message}\n")
            flash("Thank you! Your message has been sent. We will reach out shortly.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html", active="contact")


# ---------------------------------------------------------------------------
# Portal — landing with the two login choices
# ---------------------------------------------------------------------------
@app.route("/portal")
def portal():
    if session.get("user"):
        u = session["user"]
        return redirect(url_for("employee_dashboard" if u["type"] == "employee"
                                else "customer_dashboard"))
    return render_template("portal.html", active="portal")


# ----------------------- Employee login (LDAP) ----------------------------
def ldap_authenticate(username, password):
    """Authenticate against a real LDAP server when configured,
    otherwise fall back to the built-in demo directory."""
    if LDAP_SERVER:
        try:
            from ldap3 import Server, Connection, ALL
            server = Server(LDAP_SERVER, get_info=ALL)
            user_dn = f"{LDAP_USER_ATTR}={username},{LDAP_BASE_DN}"
            conn = Connection(server, user=user_dn, password=password, auto_bind=True)
            conn.unbind()
            return {"name": username, "role": "Employee"}
        except Exception:
            return None
    # Demo fallback
    acct = DEMO_EMPLOYEES.get(username)
    if acct and acct["password"] == password:
        return {"name": acct["name"], "role": acct["role"]}
    return None


@app.route("/portal/employee", methods=["GET", "POST"])
def employee_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        result = ldap_authenticate(username, password)
        if result:
            session["user"] = {"type": "employee", "username": username,
                               "name": result["name"], "role": result["role"]}
            flash(f"Welcome back, {result['name']}!", "success")
            return redirect(url_for("employee_dashboard"))
        flash("Invalid LDAP credentials. Please try again.", "danger")
    return render_template("login_employee.html", active="portal",
                           ldap_configured=bool(LDAP_SERVER))


# ----------------------- Customer login (Google) ---------------------------
@app.route("/portal/customer")
def customer_login():
    return render_template("login_customer.html", active="portal",
                           google_configured=bool(oauth))


@app.route("/auth/google")
def google_auth():
    if oauth:
        redirect_uri = url_for("google_callback", _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    # Demo mode — simulate a Google sign-in so the flow can be tested locally
    return redirect(url_for("google_demo"))


@app.route("/auth/google/callback")
def google_callback():
    if not oauth:
        return redirect(url_for("customer_login"))
    token = oauth.google.authorize_access_token()
    info = token.get("userinfo") or {}
    session["user"] = {"type": "customer",
                       "name": info.get("name", "Customer"),
                       "email": info.get("email", ""),
                       "picture": info.get("picture", "")}
    flash(f"Signed in with Google as {session['user']['name']}.", "success")
    return redirect(url_for("customer_dashboard"))


@app.route("/auth/google/demo", methods=["GET", "POST"])
def google_demo():
    """Demo Google sign-in used when no OAuth credentials are configured."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        name = request.form.get("name", "").strip() or email.split("@")[0].title()
        if "@" not in email:
            flash("Please enter a valid email address.", "warning")
        else:
            session["user"] = {"type": "customer", "name": name,
                               "email": email, "picture": ""}
            flash(f"Signed in (demo Google account) as {name}.", "success")
            return redirect(url_for("customer_dashboard"))
    return render_template("google_demo.html", active="portal")


# ----------------------- Dashboards & logout -------------------------------
@app.route("/dashboard/employee")
@login_required("employee")
def employee_dashboard():
    return render_template("dashboard_employee.html", active="portal")


@app.route("/dashboard/customer")
@login_required("customer")
def customer_dashboard():
    return render_template("dashboard_customer.html", active="portal")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# ---------------------------------------------------------------------------
# Serve image files kept in the project Images/ folder (convenience for local dev)
@app.route('/Images/<path:filename>')
def images_file(filename):
    images_dir = os.path.join(app.root_path, 'Images')
    # Provide fallbacks for filenames that may not exactly match uploaded files
    # Map friendly names to actual files present in Images/ (keep minimal)
    fallback_map = {}
    requested = filename
    full_path = os.path.join(images_dir, requested)
    if not os.path.exists(full_path):
        # direct mapping
        if requested in fallback_map:
            requested = fallback_map[requested]
            full_path = os.path.join(images_dir, requested)
        else:
            # try case-insensitive match to existing files
            for f in os.listdir(images_dir):
                if f.lower() == requested.lower():
                    requested = f
                    full_path = os.path.join(images_dir, requested)
                    break
    return send_from_directory(images_dir, requested)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
