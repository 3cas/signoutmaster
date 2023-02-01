from flask import Flask
import os

from signout import signout

# This version of app.py is designed to run the app locally. The app is contained within a blueprint, and this is done so that the same code can be run standalone as well as from my server.

DOMAIN = "localhost" 

app = Flask(__name__, subdomain_matching=True)
app.config["SERVER_NAME"] = f"{DOMAIN}:8000"
app.config["SECRET_KEY"] = os.urandom(12).hex()

app.register_blueprint(signout)

if __name__ == "__main__":
    print("running")
    import setup

    app.config["SERVER_NAME"] == "localhost:8000"
    app.run()