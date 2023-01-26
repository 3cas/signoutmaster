from flask import render_template, url_for, Blueprint
import os

# This file includes some utilities and shortcuts which are mainly useful on my main server, used in this repo for consistency.

run_dir = os.path.dirname(__file__)

def path(*targets):
    return os.path.join(run_dir, *targets)

def inst(*targets):
    return path("instance", *targets)

def util(*targets):
    return path("utility", *targets)

class BetterBlueprint(Blueprint):
    def __init__(self, name, import_name = None):
        if not import_name:
            import_name = __name__

        super().__init__(name, import_name)

    def get_static_url(self, filepath):
        return url_for("static", filename=os.path.join(self.name, filepath))

    def render(self, template, **kwargs):
        return render_template(f"{self.name}/{template}", static=self.get_static_url, **kwargs)

    def render_error(self, code, message):
        return self.render("error.html", code=code, message=message), code