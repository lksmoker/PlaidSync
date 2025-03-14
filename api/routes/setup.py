from flask import Blueprint, render_template

setup_blueprint = Blueprint("setup", __name__)

@setup_blueprint.route("/setup")
def setup_page():
    """Render the setup page for managing categories."""
    return render_template("setup.html")