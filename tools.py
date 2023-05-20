from flask import g, Blueprint, url_for, render_template, request
import requests
import os
import sqlite3
import json
import functools

# LOCAL NOTE: This file has been copied from one of my bigger web development projects. It contains a lot of redundant and unused functionality,
# but it allows me to run signout.py from my server as well.

run_dir = os.path.dirname(__file__)

# limiter = flask_limiter.Limiter(flask_limiter.util.get_remote_address)

MY_DOMAINS = ["weirdcease.com", "act25.com", "sody.win"]

def get_db(db_name):
    if not hasattr(g, "db"):
        g.db = sqlite3.connect(inst(db_name))
    return g.db

def path(*targets):
    return os.path.join(run_dir, *targets)

def inst(*targets):
    return path("instance", *targets)

def util(*targets):
    return path("utility", *targets)

with open(util("secrets.json"), "r") as f:
    SECRETS = json.load(f)

try:
    with open(inst("id.txt"), "r") as f:
        iid = f.read()
except FileNotFoundError:
    iid = "NOT FOUND"

class MyBlueprint(Blueprint):
    def __init__(self, name, import_name = None, **kwargs):
        if not import_name:
            import_name = __name__
        
        host = kwargs.pop("host", "weirdcease.com")
        database = kwargs.pop("db", None)
        database_routes = kwargs.pop("db_routes", None)
        dont_commit = kwargs.pop("dont_commit", False)
        setup_func = kwargs.pop("setup", None)

        has_domain = False
        for domain in MY_DOMAINS:
            if domain in host:
                has_domain = True
                break

        if not has_domain:
            host = host + ".weirdcease.com"
        
        self.host = host
        
        print(f"Blueprint {name} will have host {self.host}")
        self.route = functools.partial(super().route, host=self.host)
        
        if setup_func:
            setup_func()

        super().__init__(name, import_name, **kwargs)

        if database:
            self.database_routes = database_routes
            self.dont_commit = dont_commit

            self.db_file = database + ".db"
            self.db_schema = database + ".sql"

            if not os.path.isfile(inst(self.db_file)):
                print(f"Blueprint {name}: Initializing {self.db_file} with {self.db_schema}")

                with open(util(self.db_schema), "r") as f:
                    init_script = f.read()

                con = sqlite3.connect(inst(self.db_file))
                cur = con.cursor()
                cur.executescript(init_script)
                con.commit()
                con.close()

            @self.before_request
            def open_db():
                if (not self.database_routes) or (not isinstance(self.database_routes, list)) or (request.endpoint in self.database_routes):
                    g.db = get_db(self.db_file)
                    g.cur = g.db.cursor()

            @self.after_request
            def close_db(response):
                if hasattr(g, "db"):
                    if not self.dont_commit:
                        g.db.commit()
                    g.db.close()
                return response

    def get_static_url(self, filepath):
        return url_for("static", filename=os.path.join(self.name, filepath))

    def render(self, template, **kwargs):
        return render_template(f"{self.name}/{template}", static=self.get_static_url, **kwargs)

    def render_error(self, code, message):
        return self.render("error.html", code=code, message=message), code

def debug(content):
    requests.post(
        "https://discord.com/api/webhooks/1041385180117618708/6QV6Yc1ZgpUxoD-VcgFwQCn7kYjH5Aaf8JEpKXFWHNph8wEsjkCSlKXXRkxjis4yvFAA",
        json = {
            "content": content
        }
    )

def send_email(recipients: list, subject: str, body: str, category: str, sender_name: str = "weirdcease.com", sender_address: str = "no-reply@weirdcease.com"):
    payload = {
        "from": {
            "email": sender_address,
            "name": sender_name
        },
        "to": [{"email": recipient} for recipient in recipients],
        "subject": subject,
        "text": body,
        "category": category
    }

    url = "https://send.api.mailtrap.io/api/send"
    payload = json.dumps(payload)
    headers = {
        "Authorization": f"Bearer {SECRETS['mailtrap_token']}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=payload)

    return response.text

def log(message):
    print(message)
    debug(message)