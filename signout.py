from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from datetime import datetime
import json
import random

import tools
import setup

signout = Blueprint("signout", __name__)

ALLOWED_USERNAME = "abcdefghijklmnopqrstuvwxyz1234567890_-"
ALLOWED_EMAIL = "abcdefghijklmnopqrstuvwxyz1234567890!#$%&'*+-/=?^_`{}~@."

DEFAULT_SETTINGS = {
    "locations": {
        "bathroom": 10,
        "nurse": 30,
        "office": 15
    },
    "allow_other": True,
    "allow_leave": True,
    "remote_on": False,
    "remote_url": None,
    "date_format": "%m/%d",
    "time_format": "%I:%M %p",
    "id_min": 4,
    "id_max": 8
}

# NOTE: onboard is no longer an onboarding variable for new empty configs, instead, 
# configuration is initialized at account creation, and onboard is only enabled if 
# those settings are deleted or corrupted

def now(): return int(datetime.timestamp(datetime.utcnow()))
# datetime.fromtimestamp(timestamp).strftime("%m/%d/%y(%a)%H:%M:%S")

# function that checks if a user is logged in
# student: set to true when you want to allow student access, otherwise student lock denies access
# onboard: set to true when you want to allow new account access, otherwise redirects to settings
def check_user(*, student: bool = False, onboard: bool = False):
    LOGIN_ERROR = ["You must be logged in!", "signout.login"]
    STUDENT_MODE = ["This device is locked to student mode", "signout.student"]
    ONBOARD_NEEDED = ["In order to access the panel and use the service, you must set settings first!", "signout.settings"]

    # deny access if not logged in
    if "user_id" not in session or not session["user_id"]:
        return LOGIN_ERROR
    
    config = g.cur.execute(
        "SELECT config FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()[0]

    # check if any result from SQL query
    if not config:
        session.clear()
        return LOGIN_ERROR

    # deny access if locked in student mode
    if not student and "student_lock" in session and session["student_lock"]:
        return STUDENT_MODE
    
    # now we check settings to see if the service can be used
    try:
        # check if config column can be converted to dict
        settings = json.loads(config)
    except:
        # not dict-able, so we set to empty dict and stop users later
        settings = {}
        session["onboard"] = True
    else:
        # dict was in config column, check dict contents
        # VALIDATE SETTINGS HERE
        if not (
            "locations" in settings and 
            len(settings["locations"]) > 0
        ):
            session["onboard"] = True
        else:
            session["onboard"] = False

    # deny access to those who need settings ('onboard')
    if (not onboard) and session["onboard"]:
        return ONBOARD_NEEDED

    return None

# flash error and redirect, used only for session checking atm
def user_error(error: list):
    flash(error[0], "neg")
    return redirect(url_for(error[1]))

# the following code checks if a user can view the page and returns the proper error if not
# assignment operator checks if there is an error and assigns any error to the error variable
# if error := check_user(): return user_error(error)

# used to generate remote access links
def gen_remote():
    key = ""
    for i in range(64):
        key += random.choice(ALLOWED_USERNAME)
    return key

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

    if not (email and schoolname and username and password and confirm_password):
        flash("You must fill out all fields", "neg")
        return redirect(url_for("signout.register"))
    
    if not 6 <= len(email) <= 64:
        flash("Email must be between 6 and 64 characters")
        return redirect(url_for("signout.register"))
    
    if not 3 <= len(schoolname) <= 64:
        flash("School name must be between 3 and 64 characters", "neg")
        return redirect(url_for("signout.register"))
    
    if not 3 <= len(username) <= 16:
        flash("Username must be between 3 and 16 characters", "neg")
        return redirect(url_for("signout.register"))
    
    if not 8 <= len(password) <= 64:
        flash("Password must be between 8 and 64 characters", "neg")
        return redirect(url_for("signout.register"))

    for char in email:
        if char not in ALLOWED_EMAIL:
            flash("Email contains invalid characters", "neg")
            return redirect(url_for("signout.register"))

    for char in username:
        if char not in ALLOWED_USERNAME:
            flash("Username can only be a-z, 0-9, - and _,", "neg")
            return redirect(url_for("signout.register"))

    if confirm_password != password:
        flash("Passwords do not match!", "neg")
        return redirect(url_for("signout.register"))

    else:
        start_config = json.dumps(DEFAULT_SETTINGS)

        try:
            g.cur.execute(
                "INSERT INTO users (email, schoolname, username, password_hash, config) VALUES (?, ?, ?, ?, ?)",
                (email, schoolname, username, generate_password_hash(password), start_config)
            )

        except sqlite3.IntegrityError:
            flash("An account with that username, school name, or email already exists.", "neg")
            return redirect(url_for("signout.register"))

        else:
            flash(f"Account {username} successfully created. You can now login.", "pos")
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
        f"SELECT id, password_hash, username, config FROM users WHERE {ident_type} = ?", (identifier,)
    ).fetchone()

    if user:
        if check_password_hash(user[1], password):
            # fix broken config in SQL
            settings = json.loads(user[3])
            for key in DEFAULT_SETTINGS:
                if key not in user[3]:
                    settings[key] = DEFAULT_SETTINGS[key]
            if settings != user[3]:
                config = json.dumps(settings)
                g.cur.execute(
                    "UPDATE users SET config = ? WHERE id = ?",
                    (config, user[0])
                )
        
            session.clear()
            session["user_id"] = user[0]
            flash(f"Successfully logged in as {user[2]}!", "pos")
            return redirect(url_for("signout.monitor"))

        else:
            flash("Incorrect password!", "neg")
            return redirect(url_for("signout.login"))

    else:
        flash("That account doesn't exist!", "neg")
        return redirect(url_for("signout.login"))

# logout redirect
@signout.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out!", "pos")
    return redirect(url_for("signout.home"))

# /panel route has been removed, it was going to be a hub
# now navigation is handled via topbar and tabbed.html, new logins shown welcome.html (? they dont...)

# settings page
@signout.route("/panel/settings")
def settings():
    if error := check_user(onboard=True): return user_error(error)

    user = g.cur.execute(
        "SELECT username, schoolname, config FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    user_settings = json.loads(user[2])

    return render_template("settings.html", username=user[0], schoolname=user[1], settings=user_settings)

# apply settings backend
@signout.route("/settings/handler", methods=["POST"])
def apply_settings():
    if error := check_user(onboard=True): return user_error(error)

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
    set_other = request.form.get("set-other")
    set_leave = request.form.get("set-leave")
    set_remote = request.form.get("set-remote")
    regen_remote = request.form.get("regen-link")
    date_format = request.form.get("date-format")
    time_format = request.form.get("time-format")
    id_min = request.form.get("id-min")
    id_max = request.form.get("id-max")

    # apply settings

    if remove_location:
        del user_settings["locations"][remove_location]
    
    if add_location and add_location_time:
        try:
            add_time = int(add_location_time)
        except ValueError:
            flash("You must supply integer times", "neg")
            return redirect(url_for("signout.settings"))
        else:
            user_settings["locations"][add_location] = add_time

    if set_other == "0":
        user_settings["allow_other"] = False
    elif set_other == "1":
        user_settings["allow_other"] = True

    if set_leave == "0":
        user_settings["allow_leave"] = False
    elif set_leave == "1":
        user_settings["allow_leave"] = True

    if set_remote == "1":
        user_settings["remote_on"] = True
        if not user_settings["remote_url"]:
            user_settings["remote_url"] = gen_remote()
    elif set_remote == "0":
        user_settings["remote_on"] = False

    if regen_remote == "1":
        user_settings["remote_url"] = gen_remote()

    if date_format:
        user_settings["date_format"] = date_format
    
    if time_format:
        user_settings["time_format"] = time_format

    # TODO: add id min and max here and to settings.html

    # set autoscroll anchor based on which settings were changed
    anchor = None
    if date_format or time_format:
        anchor = "display"
    if set_remote or regen_remote:
        anchor = "remote"
    if remove_location or add_location or add_location_time or set_other or set_leave:
        anchor = "destinations"

    # put user settings back in database
    user_settings = json.dumps(user_settings)
    g.cur.execute(
        "UPDATE users SET config = ? WHERE id = ?",
        (user_settings, session["user_id"])
    )

    flash("Applied changes!", "pos")
    return redirect(url_for("signout.settings", _anchor=anchor))

# monitor student signouts
@signout.route("/panel/monitor")
def monitor():
    if error := check_user(): return user_error(error)

    user = g.cur.execute(
        "SELECT username, schoolname, config FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    settings = json.loads(user[2])

    try:
        signouts = g.cur.execute(
            "SELECT * FROM signouts WHERE school_id = ?",
            (session["user_id"],)
        ).fetchall()

    except:
        flash("Something went wrong when querying the database")
        curr = None
        past = None
    
    else:
        curr = []
        past = []

        for signout in signouts:
            if signout[5]:
                past.append(signout)
            else:
                curr.append(signout)

    return render_template("monitor.html", 
        username=user[0], 
        schoolname=user[1], 
        settings=settings, 
        time=now(), 
        current_signouts=curr, 
        past_signouts=past
    )

# lock panel in student mode
@signout.route("/panel/lock")
def student_lock():
    if error := check_user(): return user_error(error)
    flash("The panel has been locked in student mode", "inf")
    session["student_lock"] = True
    
    return redirect(url_for("signout.student"))

@signout.route("/panel/unlock")
def student_unlock():
    if error := check_user(student=True, onboard=True): return user_error(error)
    if "student_lock" not in session or session["student_lock"] == False:
        flash("The panel was already unlocked", "inf")
        return redirect(url_for("signout.monitor"))
    
    return render_template("unlock.html")

@signout.route("/panel/unlock/handler", methods=["POST"])
def unlock_handler():
    if error := check_user(student=True, onboard=True): return user_error(error)
    
    password = request.form.get("password")
    if not password:
        flash("Password is required", "neg")
        return redirect(url_for("signout.student_unlock"))
    
    password_hash = g.cur.execute(
        f"SELECT password_hash FROM users WHERE id = ?", 
        (session["user_id"],)
    ).fetchone()[0]

    if check_password_hash(password_hash, password):
        session["student_lock"] = False
        flash("Unlocked the panel", "pos")
        return redirect(url_for("signout.monitor"))

    flash("Incorrect password", "neg")
    return redirect(url_for("signout.student_unlock"))

# student view of panel, must re-login to be admin
@signout.route("/panel/student")
def student():
    if error := check_user(student=True): return user_error(error)

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
@signout.route("/panel/student/handler", methods=["POST"])
def student_handler():
    student_id = request.form.get("id")
    destination = request.form.get("destination")
    other = request.form.get("other")
    dismiss = request.form.get("dismiss")
    monitor = request.form.get("monitor")
    remote_key = request.form.get("remote_key")

    if monitor == "1":
        monitor = True
    else:
        monitor = False

    if remote_key:
        school_id = g.cur.execute(
            "SELECT id FROM users WHERE config LIKE ?",
            (f'%"remote_url": "{remote_key}"%',)
        ).fetchone()[0]

        if school_id:
            skip_check = True
            monitor = False

        else:
            skip_check = False

    else:
        skip_check = False

    if not skip_check:
        if error := check_user(student=True): return user_error(error)
        school_id = session["user_id"]

    if monitor and not check_user():
        redir = url_for("signout.monitor")
    elif remote_key:
        redir = url_for("signout.remote_link", key=remote_key)
    else:
        redir = url_for("signout.student")

    redir = redirect(redir)

    if not (student_id and destination):
        flash("Not enough parameters", "neg")
        return redir
    
    if destination == "return":
        try:
            g.cur.execute(
                "UPDATE signouts SET time_in = ? WHERE school_id = ? AND student_id = ?",
                (now(), school_id, student_id)
            )
        
        except:
            if monitor:
                message = f"Error! {student_id} was not signed out."
            else:
                message = f"{student_id}: Error! You were not signed out."
            color = "neg"

        else:
            if monitor:
                message = f"{student_id} has been signed back in."
            else:
                message = f"{student_id}: You have been signed back in."
            color = "pos"

        flash(message, color)        
        return redir

    if destination == "other":
        if other:
            destination = other

    try:
        g.cur.execute(
            "INSERT INTO signouts (school_id, student_id, location, time_out) VALUES (?, ?, ?, ?)",
            (school_id, student_id, destination, now())
        )
    
    except:
        if monitor:
            message = f"{student_id}: This is about the worst error you could ever get. Something has gone horrible awry."
        else:
            message = f"{student_id}: Sorry, something went wrong signing out."
        color = "neg"
    
    else:
        if monitor:
            message = f"You weren't supposed to do that. Nonetheless, {student_id} has been signed out to {destination}..."
        else:
            message = f"{student_id}: You have signed out to {destination}"
        color = "pos"

    flash(message, color)
    return redir

@signout.route("/panel/monitor/clearall")
def clear_signouts():
    if error := check_user(): return user_error(error)

    try:
        g.cur.execute(
            "DELETE FROM signouts WHERE school_id = ?",
            (session["user_id"],)
        )
    
    except:
        flash("Something went wrong lol", "neg")
    else:
        flash("Something went RIGHT!", "pos")

    return redirect(url_for("signout.monitor"))

# unimplemented share link feature
@signout.route("/remote/<key>")
def remote_link(key):
    user = g.cur.execute(
        "SELECT schoolname, config FROM users WHERE config LIKE ?",
        (f'%"remote_url": "{key}"%',)
    ).fetchone()

    if user:
        settings = json.loads(user[1])

        if settings["remote_on"]:
            return render_template("student.html", 
                schoolname=user[0], 
                time=now(), 
                settings=settings, 
                remote_key=key
            )
    
    return "The link you followed was invalid!"

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

# commit and close database connection, do not cache
@signout.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, post-check=0, pre-check=0"
    if hasattr(g, "db"):
        g.db.commit()
        g.db.close()
    return response