from flask import Blueprint, render_template, url_for
from app.models import Trek, User, Booking
from flask_login import current_user
main = Blueprint('main', __name__)


@main.route("/")
def home():

    dashboard_url = None

    if current_user.is_authenticated:
        if current_user.role == "ADMIN":
            dashboard_url = url_for("admin.dashboard")
        elif current_user.role == "STAFF":
            dashboard_url = url_for("staff.dashboard")
        else:
            dashboard_url = url_for("user.dashboard")

    featured_treks = Trek.query.filter_by(status="Open").limit(10).all()
    total_users = User.query.count()
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()
    total_staff = User.query.filter_by(role="STAFF").count()

    return render_template("auth/landing.html", featured_treks=featured_treks, total_users=total_users, total_treks=total_treks, total_bookings=total_bookings, total_staff=total_staff, dashboard_url=dashboard_url)

@main.route("/about")
def about():
    return render_template("auth/about.html")


@main.route("/contact")
def contact():
    return render_template("auth/contact.html")


@main.route("/faq")
def faq():
    return render_template("auth/faq.html")


@main.route("/privacy")
def privacy():
    return render_template("auth/privacy.html")


@main.route("/terms")
def terms():
    return render_template("auth/terms.html")


@main.route("/safety")
def safety():
    return render_template("auth/safety.html")