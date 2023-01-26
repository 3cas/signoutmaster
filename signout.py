from flask import Blueprint, render_template
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
    return "register now"

@signout.route("/new-registration", methods=["POST"])
def new_admin():
    return "new admin account"

@signout.route("/panel")
def panel():
    return "signed in panel"

@signout.route("/panel/settings")
def settings():
    return "settings page"

@signout.route("/panel/monitor")
def monitor():
    return "monitoring page"

@signout.route("/panel/student")
def student():
    return "student panel"