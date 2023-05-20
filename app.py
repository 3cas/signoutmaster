from flask import Flask
import os

from signout import signout

# This version of app.py is designed to run the app locally. The app is contained within a blueprint.
# This is done so that the same code can be run standalone as well as from my server (signout.act25.com).

app = Flask(__name__, subdomain_matching=True)
app.config["SECRET_KEY"] = os.urandom(12).hex()

app.register_blueprint(signout)

if __name__ == "__main__":
    app.run()