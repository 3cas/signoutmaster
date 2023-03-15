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

def now(): return int(datetime.timestamp(datetime.utcnow()))
# datetime.fromtimestamp(timestamp).strftime("%m/%d/%y(%a)%H:%M:%S")

# function that checks if a user is logged in
def check_user(can_view_as_student: bool = False):
    LOGIN_ERROR = ["You must be logged in!", "signout.login"]
    STUDENT_MODE = ["This device is locked to student mode", "signout.student"]

    if "user_id" not in session or not session["user_id"]:
        return LOGIN_ERROR
    
    user = g.cur.execute(
        "SELECT username FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if not user:
        session.clear()
        return LOGIN_ERROR

    if not can_view_as_student and "student_lock" in session and session["student_lock"]:
        return STUDENT_MODE

    return None

# flash error and redirect, used only for session checking atm
def user_error(error: list):
    flash(error[0], "error")
    return redirect(url_for(error[1]))

# the following code checks if a user can view the page and returns the proper error if not
# assignment operator checks if there is an error and assigns any error to the error variable
# if error := check_user(): return user_error(error)

# connect to database before every request
@signout.before_request
def before_request():
    g.db = tools.get_db("signout.db")
    g.cur = g.db.cursor()

# home page
@signout.route("/")
@signout.route("/home")
def home():
    if not check_user():
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
    if error := check_user(): return user_error(error)

    user = g.cur.execute(
        "SELECT username, schoolname, config FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    
    username = user[0]
    schoolname = user[1]
    settings = user[2]

    try:
        settings = json.loads(settings)
    except:
        settings = {}
        onboard = True
    else:
        if not (
            "locations" in settings and 
            len(settings["locations"]) > 0
        ):
            onboard = True
        else:
            onboard = False

    return render_template("panel.html", username=username, schoolname=schoolname, onboard=onboard)

# onboarding settings (?)
@signout.route("/panel/onboarding")
def onboarding():
    return render_template("onboarding.html")

# settings page
@signout.route("/panel/settings")
def settings():
    if error := check_user(): return user_error(error)

    user_settings = g.cur.execute(
        "SELECT config FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()[0]
    user_settings = json.loads(user_settings)

    return render_template("settings.html", settings=user_settings)

# apply settings backend
@signout.route("/panel/settings/apply", methods=["POST"])
def apply_settings():
    if error := check_user(): return user_error(error)

    # get dictionary of user settings
    user_settings = g.cur.execute(
        "SELECT config FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()[0]
    user_settings = json.loads(user_settings)

    # initialize user settings
    if "locations" not in user_settings:
        user_settings["locations"] = {}

    # get all optional settings parameters
    remove_location = request.form.get("remove-location")
    add_location = request.form.get("add-location")
    add_location_time = request.form.get("add-location-time")

    # apply settings

    if remove_location:
        del user_settings["locations"][remove_location]
    
    if add_location and add_location_time:
        user_settings["locations"][add_location] = add_location_time

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
    if error := check_user(): return user_error(error)

    return render_template("monitor.html")

# lock panel in student mode
@signout.route("/panel/lock")
def student_lock():
    if error := check_user(): return user_error(error)
    flash("The panel has been locked in student mode", "message")
    session["student_lock"] = True
    
    return redirect(url_for("signout.student"))

# student view of panel, must re-login to be admin
@signout.route("/panel/student")
def student():
    if error := check_user(True): return user_error(error)

    user = g.cur.execute(
        "SELECT schoolname, config FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    schoolname = user[0]
    settings = user[1]
    settings = json.loads(settings)

    time = datetime.utcnow().strftime("%-I:%M %p")

    return render_template("student.html", schoolname=schoolname, time=time, settings=settings)

# student panel signout or in backend
@signout.route("/panel/student/sign", methods=["POST"])
def sign():
    if error := check_user(True): return user_error(error)

    student_id = request.form.get("id")
    destination = request.form.get("destination")
    other = request.form.get("other")
    dismiss = request.form.get("dismiss")

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

# commit and close database connection,  do not cache
@signout.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, post-check=0, pre-check=0"
    if hasattr(g, "db"):
        g.db.commit()
        g.db.close()
    return response