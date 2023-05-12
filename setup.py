import os
import sqlite3
from werkzeug.security import generate_password_hash

if not os.path.isdir("instance"):
    os.mkdir("instance")
    print("Instance directory was created")

if not os.path.isfile("instance/signout.db"):
    with open("signout.sql", "r") as f:
        init_script = f.read()

    con = sqlite3.connect("instance/signout.db")
    cur = con.cursor()

    cur.executescript(init_script)
    cur.execute(
        "INSERT INTO users (email, schoolname, password_hash) VALUES (?, ?, ?)",
        ("admin", "test school", generate_password_hash("admin"))
    )

    con.commit()
    con.close()