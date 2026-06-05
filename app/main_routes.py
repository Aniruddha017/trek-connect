from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route("/")
def home():
    return """
    <h1>Trekking Management App</h1>

    <a href="/treks">View Treks</a><br>
    <a href="/register">Register</a><br>
    <a href="/login">Login</a>
    """

@main.route("/treks")
def treks():
    return "<h2>Available Treks will be shown here</h2>"
