from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

import tools

con = sqlite3.connect(tools.inst("signout.db"))
cur = con.cursor()

signout = Blueprint("signout", __name__)

@signout.route("/")
def home():
    return render_template("home.html")

@signout.route("/register")
def register():
    return render_template("register.html")

@signout.route("/register/handler", methods=["POST"])
def register_handler():
    username = request.form.get("username")
    password = request.form.get("password")

    cur.execute(
        "INSERT INTO users (username, password_hash, config) VALUES (?, ?, ?)",
        (username, generate_password_hash(password), "{}")
    )
    con.commit()
    
    flash("Account {username} successfully created. You can now login.")
    return redirect(url_for("signout.login"))

@signout.route("/login")
def login():
    return render_template("login.html")

@signout.route("/login/handler", methods=["POST"])
def login_hander():
    username = request.form.get("username")
    password = request.form.get("password")

    user = cur.execute(
        "SELECT * FROM user WHERE username = ?", (username,)
    ).fetchone()

    if user:
        if check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("signout.panel"))

        flash("Incorrect password!")

    flash("That account doesn't exist!")

    return redirect(url_for("signout.login"))

@signout.route("/panel")
def panel():
    return render_template("panel.html")

@signout.route("/panel/settings")
def settings():
    return render_template("settings.html")

@signout.route("/panel/settings/apply")
def apply_settings():
    # ...
    flash("Applied changes!")
    return redirect(url_for("signout.settings"))

@signout.route("/panel/monitor")
def monitor():
    return "monitoring page"

@signout.route("/panel/student")
def student():
    return "student panel"

@signout.route("/panel/sign")
def sign():
    return "signing out or in"

@signout.route("/share/<public_id>")
def student_public(public_id):
    return "student panel public share link"