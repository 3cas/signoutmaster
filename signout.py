from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from datetime import datetime
import json

import tools
import setup

signout = Blueprint("signout", __name__)

ALLOWED_USERNAME = "abcdefghijklmnopqrstuvwxyz1234567890_-"
ALLOWED_EMAIL = "abcdefghijklmnopqrstuvwxyz1234567890!#$%&'*+-/=?^_`{|}~@."

def now(): return int(datetime.timestamp(datetime.now()))

# function that checks if a user exists
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

# redirect to login page
def no_user():
    flash("You must be logged in!", "error")
    return redirect(url_for("signout.login"))

# if not check_user(): return no_user()

# connect to database before every request
@signout.before_request
def before_request():
    g.db = tools.get_db("signout.db")
    g.cur = g.db.cursor()

# split() functionality within templates
@signout.app_template_filter("split")
def my_split(text: str, splitter: str):
    return text.split(splitter)

# do not cache page
@signout.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, post-check=0, pre-check=0"
    return response

# home page
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

# register view
@signout.route("/register")
def register():
    return render_template("register.html")

# register backend
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
            flash("Username can only be a-z, 0-9, - and _,", "error")
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

# login view
@signout.route("/login")
def login():
    return render_template("login.html")

# login backend
@signout.route("/login/handler", methods=["POST"])
def login_handler():
    identifier = request.form.get("identifier").lower()
    password = request.form.get("password")

    ident_type = "email" if "@" in identifier else "username"

    user = g.cur.execute(
        f"SELECT id, password_hash, username FROM users WHERE {ident_type} = ?", (identifier,)
    ).fetchone()

    if user:
        if check_password_hash(user[1], password):
            session.clear()
            session["user_id"] = user[0]
            flash(f"Successfully logged in as {user[2]}!", "success")
            return redirect(url_for("signout.panel"))

        else:
            flash("Incorrect password!", "error")
            return redirect(url_for("signout.login"))

    else:
        flash("That account doesn't exist!", "error")
        return redirect(url_for("signout.login"))

# logout redirect
@signout.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out!", "success")
    return redirect(url_for("signout.home"))

# panel with settings, monitor, student view, and logout
@signout.route("/panel")
def panel():
    if not check_user(): return no_user()

    user = g.cur.execute(
        "SELECT username, schoolname, config FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    user = list(user)

    try:
        user[2] = json.loads(user[2])
    except:
        user[2] = {}

    return render_template("panel.html", user=user)

# onboarding settings (?)
@signout.route("/panel/onboarding")
def onboarding():
    return render_template("onboarding.html")

# settings page
@signout.route("/panel/settings")
def settings():
    if not check_user(): return no_user()

    user_settings = g.cur.execute(
        "SELECT config FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()[0]
    user_settings = json.loads(user_settings)

    return render_template("settings.html", settings=user_settings)

# apply settings backend
@signout.route("/panel/settings/apply", methods=["POST"])
def apply_settings():
    if not check_user(): return no_user()

    # get all optional settings parameters
    remove_location = request.form.get("remove-location")
    add_location = request.form.get("add-location")
    add_location_time = request.form.get("add-location-time")

    # get dictionary of user settings
    user_settings = g.cur.execute(
        "SELECT config FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()[0]
    user_settings = json.loads(user_settings)

    # initialize user settings
    if "locations" not in user_settings:
        user_settings["locations"] = []

    # apply settings

    if remove_location:
        for location in user_settings["locations"]:
            if location[0] == remove_location:
                user_settings["locations"].remove(location)
    
    if add_location:
        user_settings["locations"].append([add_location, add_location_time])

    # put user settings back in database
    user_settings = json.dumps(user_settings)
    g.cur.execute(
        "UPDATE users SET config = ? WHERE id = ?",
        (user_settings, session["user_id"])
    )

    flash("Applied changes!", "success")
    return redirect(url_for("signout.settings"))

# monitor student signouts
@signout.route("/panel/monitor")
def monitor():
    if not check_user(): return no_user()

    return "monitoring page"

# student view of panel, must re-login to be admin
@signout.route("/panel/student")
def student():
    if not check_user(): return no_user()

    return "student panel"

# student panel signout or in backend
@signout.route("/panel/student/sign", methods=["POST"])
def sign():
    if not check_user(): return no_user()

    return "signing out or in"

# unimplemented share link feature
@signout.route("/share/<public_id>")
def student_public(public_id):
    return "student panel public share link"

# wip username/email/etc taken checker
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

# commit and close database connection 
@signout.after_request
def after_request(response):
    if hasattr(g, "db"):
        g.db.commit()
        g.db.close()
    return response