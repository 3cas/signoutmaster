import os
import sqlite3

if not os.path.isdir("instance"):
    os.mkdir("instance")
    print("Instance directory was created")

if not os.path.isfile("instance/signout.db"):
    with open("signout.sql", "r") as f:
        init_script = f.read()

    con = sqlite3.connect("instance/signout.db")
    cur = con.cursor()
    cur.executescript(init_script)
    con.commit()
    con.close()