from flask import Blueprint, render_template, redirect, url_for, abort, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from utils.decorators import allowed_roles
from utils.constants import ALLOWED_STAFF_STATUSES
from app.models import User, Trek, StaffNotification 
from app import db
from datetime import date
from werkzeug.utils import secure_filename
import os
import uuid

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

@staff.route("/treks")
@login_required
@allowed_roles("STAFF")
def my_treks():
    
    treks = current_user.assigned_treks

    return render_template("staff/my_treks.html", treks=treks)


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

    if status == "Ongoing" and date.today() < trek.start_date:
        flash("A trek can only be marked as ongoing on or after its start date.", "danger")
        return redirect(url_for("staff.trek_details", trek_id=trek.id))
    
    if trek.status == "Completed":
        flash("Completed treks cannot be modified.", "danger")
        return redirect(url_for("staff.trek_details", trek_id=trek.id))
    
    if trek.status == "Ongoing":
        flash("An ongoing trek cannot be changed back to another status.", "danger")
        return redirect(url_for("staff.trek_details", trek_id=trek.id))
        
    if status == "Ongoing" and trek.status != "Closed":
        flash("Only closed treks can be marked as ongoing.", "danger")
        return redirect(url_for("staff.trek_details", trek_id=trek.id))

    trek.status = status

    db.session.commit()
    flash("Status updated", "success")

    return redirect(url_for("staff.trek_details", trek_id=trek.id))

@staff.route("/treks/<int:trek_id>/update-slots", methods=["POST"])
@login_required
@allowed_roles("STAFF")
def update_slots(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    verify_staff_access(trek)

    total_slots = request.form["total_slots"]

    if not total_slots.isdigit():
        flash("Enter valid value in total slots", "danger")
        return redirect(url_for("staff.trek_details", trek_id=trek_id))
    
    if trek.status in ("Ongoing", "Completed"):
        flash("Slots cannot be modified after the trek has started.", "danger")
        return redirect(url_for("staff.trek_details", trek_id=trek.id))
    
    total_slots = int(total_slots)

    booked_slots = trek.total_slots - trek.available_slots
    
    if total_slots < 0:
        flash("Slots cannot be negative.", "danger")
        return redirect(url_for("staff.trek_details", trek_id=trek.id))

    if total_slots < booked_slots:
        flash(f"Total slots cannot be less than already booked slots(current bookings: {booked_slots})", "danger")
        return redirect(url_for("staff.trek_details", trek_id=trek.id))

    trek.available_slots = total_slots - booked_slots
    trek.total_slots = total_slots

    db.session.commit()

    flash("Total slots updated successfully!", "success")

    return redirect(url_for("staff.trek_details", trek_id=trek.id))


@staff.route("/treks/<int:trek_id>/complete", methods=["POST"])
@login_required
@allowed_roles("STAFF")
def complete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    verify_staff_access(trek)

    if trek.end_date > date.today():
        flash("You can complete the trek only after its end date.", "danger")
        return redirect(url_for("staff.trek_details", trek_id=trek.id))
    
    if trek.status == "Completed":
        flash("This trek is already completed.", "warning")
        return redirect(url_for("staff.trek_details", trek_id=trek.id))

    trek.status = "Completed"

    for booking in trek.bookings:
        if booking.status == "Booked":
            booking.status = "Completed"

    db.session.commit()
    flash("Trek marked as completed!", "success")
    return redirect(url_for("staff.trek_details", trek_id=trek.id))


@staff.route("/profile", methods=["GET", "POST"])
@login_required
@allowed_roles("STAFF")
def profile():

    profile = current_user.staff_profile

    if request.method == "POST":

        name = request.form["name"].strip()
        mobile_number = request.form["mobile_number"].strip()
        specialization = request.form["specialization"].strip()
        experience_years = request.form.get("experience_years", "")
        image = request.files.get("profile_image")

        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not name:
            flash("Name cannot be empty.", "danger")
            return redirect(url_for("staff.profile"))

        if not mobile_number:
            flash("Mobile number is required.", "danger")
            return redirect(url_for("staff.profile"))

        if not mobile_number.isdigit():
            flash("Only numbers allowed in mobile number.", "danger")
            return redirect(url_for("staff.profile"))
        
        if not experience_years.isdigit():
            flash("enter valid experience year")
            return redirect(url_for("staff.profile"))
        
        experience_years = int(experience_years)

        if len(mobile_number) < 8:
            flash("Mobile number is too short.", "danger")
            return redirect(url_for("staff.profile"))

        if experience_years < 0:
            flash("Enter valid experience year.", "danger")
            return redirect(url_for("staff.profile"))
        
        if len(specialization) > 100:
            flash("Maximum 100 characters allowed.", "danger")
            return redirect(url_for("staff.profile"))

        existing_user = User.query.filter(
            User.mobile_number == mobile_number,
            User.id != current_user.id
        ).first()

        if existing_user:
            flash("Mobile number already exists.", "danger")
            return redirect(url_for("staff.profile"))

        current_user.name = name
        current_user.mobile_number = mobile_number

        profile.specialization = specialization
        profile.experience_years = experience_years

        if password:

            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return redirect(url_for("staff.profile"))

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return redirect(url_for("staff.profile"))

            current_user.password_hash = generate_password_hash(password)

        if image and image.filename:
            
            filename = f"{uuid.uuid4().hex}_{secure_filename(image.filename)}"

            extension = filename.rsplit(".", 1)[1].lower()

            if extension not in ["jpg", "jpeg", "png"]:
                flash("Only JPG and PNG images are allowed.", "danger")
                return redirect(url_for("staff.profile"))
            

            image.save(os.path.join("app/static/uploads/profile_images", filename))

            profile.profile_image = filename

        db.session.commit()

        flash("Profile updated successfully.", "success")
        return redirect(url_for("staff.profile"))

    return render_template(
        "staff/profile.html",
        profile=profile
    )

@staff.route("/notifications")
@login_required
@allowed_roles("STAFF")
def notifications():

    notifications = (
        StaffNotification.query
        .filter_by(staff_id=current_user.id)
        .order_by(StaffNotification.created_at.desc())
        .limit(30)
        .all()
    )    

    for notification in notifications:
        notification.is_read = True

    db.session.commit()

    return render_template("staff/notifications.html", notifications=notifications[:30])