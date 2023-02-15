from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from datetime import datetime

import tools
import setup

signout = Blueprint("signout", __name__)

ALLOWED_USERNAME = "abcdefghijklmnopqrstuvwxyz1234567890_-"
ALLOWED_EMAIL = "abcdefghijklmnopqrstuvwxyz1234567890_-@+~."

def now(): return int(datetime.timestamp(datetime.now()))

def check_user():
    if ("user_id" not in session) or (not session["user_id"]):
        return False
    
    user = g.cur.execute(
        "SELECT username FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if not user:
        session.clear()
        return False

    return True

def no_user():
    flash("You must be logged in!", "error")
    return redirect(url_for("signout.login"))

# if not check_user(): return no_user()

@signout.before_request
def before_request():
    g.db = tools.get_db("signout.db")
    g.cur = g.db.cursor()

@signout.app_template_filter("split")
def my_split(text: str, splitter: str):
    return text.split(splitter)

@signout.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, post-check=0, pre-check=0"
    return response

@signout.route("/")
@signout.route("/home")
def home():
    if check_user():
        username = g.cur.execute(
            "SELECT username FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()[0]
    else:
        username = None

    return render_template("home.html", username=username)

@signout.route("/register")
def register():
    return render_template("register.html")

@signout.route("/register/handler", methods=["POST"])
def register_handler():
    email = request.form.get("email").lower()
    schoolname = request.form.get("schoolname")
    username = request.form.get("username").lower()
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    for char in email:
        if char not in ALLOWED_EMAIL:
            flash("Email contains invalid characters", "error")
            return redirect(url_for("signout.register"))

    for char in username:
        if char not in ALLOWED_USERNAME:
            flash("Username can only be a-z, 0-9, - and _")
            return redirect(url_for("signout.register"))

    if confirm_password != password:
        flash("Passwords do not match!", "error")
        return redirect(url_for("signout.register"))

    else:
        try:
            g.cur.execute(
                "INSERT INTO users (email, schoolname, username, password_hash) VALUES (?, ?, ?, ?)",
                (email, schoolname, username, generate_password_hash(password))
            )

        except sqlite3.IntegrityError:
            flash("An account with that username, school name, or email already exists.", "error")
            return redirect(url_for("signout.register"))

        else:
            flash(f"Account {username} successfully created. You can now login.", "success")
            return redirect(url_for("signout.login"))

@signout.route("/login")
def login():
    return render_template("login.html")

@signout.route("/login/handler", methods=["POST"])
def login_handler():
    username = request.form.get("username").lower()
    password = request.form.get("password")

    user = g.cur.execute(
        "SELECT id, password_hash FROM users WHERE username = ?", (username,)
    ).fetchone()

    if user:
        if check_password_hash(user[1], password):
            session.clear()
            session["user_id"] = user[0]
            flash(f"Successfully logged in as {username}!", "success")
            return redirect(url_for("signout.panel"))

        else:
            flash("Incorrect password!", "error")
            return redirect(url_for("signout.login"))

    else:
        flash("That account doesn't exist!", "error")
        return redirect(url_for("signout.login"))

@signout.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out!", "success")
    return redirect(url_for("signout.home"))

@signout.route("/panel")
def panel():
    if not check_user(): return no_user()

    user = g.cur.execute(
        "SELECT username, config FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    username = user[0]
    try:
        config = dict(user[1])
    except:
        config = {}

    return render_template("panel.html", username=username, config=config)

@signout.route("/panel/onboarding")
def onboarding():
    return render_template("onboarding.html")

@signout.route("/panel/settings")
def settings():
    if not check_user(): return no_user()

    return render_template("settings.html")

@signout.route("/panel/settings/apply")
def apply_settings():
    if not check_user(): return no_user()
    # ...
    flash("Applied changes!", "success")
    return redirect(url_for("signout.settings"))

@signout.route("/panel/monitor")
def monitor():
    if not check_user(): return no_user()

    return "monitoring page"

@signout.route("/panel/student")
def student():
    if not check_user(): return no_user()

    return "student panel"

@signout.route("/panel/sign", methods=["POST"])
def sign():
    if not check_user(): return no_user()

    return "signing out or in"

@signout.route("/share/<public_id>")
def student_public(public_id):
    return "student panel public share link"

@signout.route("/check")
def check_available():
    field = request.args.get("field")
    value = request.args.get("value")

    if not (field or value):
        return "not enough arguments"
    
    if field not in ["email", "schoolname", "username"]:
        return "invalid field"

    result = g.cur.execute(
        f"SELECT id FROM users WHERE {field} = ?",
        (value,)
    )

    if result:
        return "taken"
    else:
        return "free"

@signout.after_request
def after_request(response):
    if hasattr(g, "db"):
        g.db.commit()
        g.db.close()
    return response