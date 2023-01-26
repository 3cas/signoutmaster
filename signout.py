from flask import Blueprint, render_template, request, redirect, url_for, session, g
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
    
    return redirect(url_for("signout.login", fillname=username, message=f"Account {username} successfully created. You can now login."))

@signout.route("/login")
def login():
    message = request.args.get("message")
    fillname = request.args.get("fillname")
    return render_template("login.html", fillname=fillname, message=message)

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

        else:
            return redirect(url_for("signout.login", message="Incorrect password!"))

    else:
        return redirect(url_for("signout.login", message="That account doesn't exist!"))

@signout.route("/panel")
def panel():
    message = request.args.get("message")
    return render_template("panel.html", message=message)

@signout.route("/panel/settings")
def settings():
    return "settings page"

@signout.route("/panel/settings/apply")
def apply_settings():
    return "apply settings"

@signout.route("/panel/monitor")
def monitor():
    return "monitoring page"

@signout.route("/panel/student")
def student():
    return "student panel"

@signout.route("/share/<public_id>")
def student_public():
    return "student panel public share link"