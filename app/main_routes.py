from flask import Blueprint, render_template
from app.models import Trek, User, Booking
main = Blueprint('main', __name__)


@main.route("/")
def home():

    featured_treks = Trek.query.filter_by(status="Open").limit(10).all()
    total_users = User.query.count()
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()
    total_staff = User.query.filter_by(role="STAFF").count()

    return render_template("auth/landing.html", featured_treks=featured_treks, total_users=total_users, total_treks=total_treks, total_bookings=total_bookings, total_staff=total_staff)

@main.route("/treks")
def treks():
    return "<h2>Available Treks will be shown here</h2>"

