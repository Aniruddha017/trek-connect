from flask import Blueprint, render_template, redirect, url_for, abort, request, flash
from flask_login import login_required, current_user
from utils.decorators import allowed_roles
from utils.constants import ALLOWED_STAFF_STATUSES
from app.models import User, Trek 
from app import db

staff = Blueprint("staff", __name__, url_prefix="/staff")

def verify_staff_access(trek):
    if current_user not in trek.assigned_staff:
        abort(403)


@staff.route("/dashboard")
@login_required
@allowed_roles("STAFF")
def dashboard():
    treks = current_user.assigned_treks
    trek_count = len(treks)
    participants_count = sum(len(trek.bookings) for trek in treks)

    return render_template("staff/dashboard.html",treks=treks, trek_count=trek_count, participants_count=participants_count)

@staff.route("/treks/<int:trek_id>")
@login_required
@allowed_roles("STAFF")
def trek_details(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    verify_staff_access(trek)

    return render_template("staff/trek_details.html", trek=trek)

@staff.route("/treks/<int:trek_id>/participants")
@login_required
@allowed_roles("STAFF")
def participants(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    verify_staff_access(trek)

    return render_template("staff/participants.html", trek=trek)

@staff.route("/treks/<int:trek_id>/update-status", methods=["POST"])
@login_required
@allowed_roles("STAFF")
def update_status(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    verify_staff_access(trek)

    status = request.form["status"]
    if status not in ALLOWED_STAFF_STATUSES:
        abort(400)
    trek.status = status

    db.session.commit()
    flash("Status updated", "success")

    return redirect(url_for("staff.trek_details", trek_id=trek.id))


@staff.route("/treks/<int:trek_id>/complete", methods=["POST"])
@login_required
@allowed_roles("STAFF")
def complete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    verify_staff_access(trek)

    trek.status = "Completed"

    for booking in trek.bookings:
        if booking.status == "Booked":
            booking.status = "Completed"

    db.session.commit()
    
    return redirect(url_for("staff.trek_details", trek_id=trek.id))




