from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from app import db
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from utils.decorators import allowed_roles
from app.models import Trek, User, Booking, StaffProfile, StaffNotification
from datetime import date
from sqlalchemy import or_
from utils import constants

user = Blueprint("user", __name__, url_prefix="/user")

def validate_booking(user, trek):

    existing = Booking.query.filter(
        Booking.user_id == user.id,
        Booking.trek_id == trek.id,
        Booking.status.in_(["Booked", "Completed"])
    ).first()

    if existing:
        return "You have already booked this trek!"

    if trek.status != "Open":
        return "Trek not open for booking!"

    if trek.available_slots <= 0:
        return "No slots available in this trek."

    if user.is_blacklisted:
        return "Blacklisted users cannot book any trek!"

    if trek.start_date <= date.today():
        return "This trek already started."

    return None


def create_booking(user, trek):

    booking = Booking(
        user_id=user.id,
        trek_id=trek.id,
        status="Booked",
        payment_status="Paid"
    )

    trek.available_slots -= 1

    db.session.add(booking)

    for staff in trek.assigned_staff:
        db.session.add(StaffNotification(staff_id=staff.id, message=f"{current_user.name} booked {trek.name}."))

    db.session.commit()


@user.route("/dashboard")
@login_required
@allowed_roles("TREKKER", "STAFF")
def dashboard():

    open_treks = Trek.query.filter_by(status="Open").all()
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    quick_view = Trek.query.filter_by(status="Open").order_by(Trek.start_date).limit(3).all()

    return render_template("user/dashboard.html", open_treks=open_treks, bookings=bookings, quick_view=quick_view)


@user.route("/treks")
@login_required
@allowed_roles("TREKKER", "STAFF")
def treks():

    search = request.args.get("search", "").strip()
    difficulty = request.args.get("difficulty", "").strip()

    query = Trek.query.filter_by(status="Open")

    if search:
        query = query.filter(or_(Trek.name.ilike(f"%{search}%"),
                                 Trek.location.ilike(f"%{search}%"),
                                 Trek.difficulty.ilike(f"%{search}%")))

    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)

    treks = query.order_by(Trek.start_date).all()        

    return render_template("user/treks.html", treks=treks, difficulties=constants.TREK_DIFFICULTIES)



@user.route("/trek/<int:trek_id>/details")
@login_required
@allowed_roles("TREKKER", "STAFF")
def trek_details(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    return render_template("user/trek_details.html", trek=trek)



@user.route("/treks/<int:trek_id>/book")
@login_required
@allowed_roles("TREKKER", "STAFF")
def book_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    error = validate_booking(current_user, trek)

    if error:
        flash(error, "danger")
        return redirect(url_for("user.trek_details", trek_id=trek.id))

    return redirect(url_for("user.payment", trek_id=trek.id))

@user.route("/payment/<int:trek_id>", methods=["GET", "POST"])
@login_required
@allowed_roles("TREKKER", "STAFF")
def payment(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    error = validate_booking(current_user, trek)

    if error:
        flash(error, "danger")
        return redirect(url_for("user.trek_details", trek_id=trek.id))

    if request.method == "POST":

        payment_method = request.form.get("payment_method")

        if not payment_method:
            flash("Please select a payment method.", "danger")
            return redirect(url_for("user.payment", trek_id=trek.id))

        error = validate_booking(current_user, trek)

        if error:
            flash(error + "If money was deducted, you can contact us for refund.", "danger")
            return redirect(url_for("user.trek_details", trek_id=trek.id))

        create_booking(current_user, trek)

        flash("Payment successful! Trek booked successfully.", "success")
        return redirect(url_for("user.bookings"))

    return render_template("user/payment.html", trek=trek)


@user.route("/bookings")
@login_required
@allowed_roles("TREKKER", "STAFF")
def bookings():
    
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template("user/bookings.html", bookings=bookings)


@user.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
@allowed_roles("TREKKER", "STAFF")
def cancel_booking(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        abort(403)
    
    trek = Trek.query.get_or_404(booking.trek_id)
    
    if booking.status != "Booked":
        flash("Only active bookings can be cancelled.", "warning")
        return redirect(url_for("user.bookings"))
    
    if trek.start_date <= date.today():
        flash("Cancellation period ended!", "danger")
        return redirect(url_for("user.bookings"))
    
    booking.status = "Cancelled"

    for staff in trek.assigned_staff:
        db.session.add(StaffNotification(staff_id=staff.id, message=f"{current_user.name} cancelled {trek.name}."))

    trek.available_slots +=1
    db.session.commit()

    flash("Booking cancelled successfully. Reach out to support for refund!","success")
    return redirect(url_for("user.bookings"))



@user.route("/history")
@login_required
@allowed_roles("TREKKER", "STAFF")
def history():
    bookings = Booking.query.filter(Booking.user_id==current_user.id, Booking.status.in_(["Completed", "Cancelled"])).order_by(Booking.booking_date.desc()).all()

    return render_template("user/history.html", bookings=bookings)


@user.route("/profile", methods=["GET", "POST"])
@login_required
@allowed_roles("TREKKER", "STAFF")
def profile():

    if request.method == "POST":

        name = request.form["name"].strip()
        mobile_number = request.form["mobile_number"].strip()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not name:
            flash("Name cannot be empty.", "danger")
            return redirect(url_for("user.profile"))

        if not mobile_number:
            flash("Mobile number is required.", "danger")
            return redirect(url_for("user.profile"))

        if not mobile_number.isdigit():
            flash("Only numbers allowed in mobile number.", "danger")
            return redirect(url_for("user.profile"))

        if len(mobile_number) < 8:
            flash("Mobile number is too short.", "danger")
            return redirect(url_for("user.profile"))

        existing_user = User.query.filter(
            User.mobile_number == mobile_number,
            User.id != current_user.id
        ).first()

        if existing_user:
            flash("Mobile number already exists.", "danger")
            return redirect(url_for("user.profile"))

        current_user.name = name
        current_user.mobile_number = mobile_number

        if password:

            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return redirect(url_for("user.profile"))

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return redirect(url_for("user.profile"))

            current_user.password_hash = generate_password_hash(password)

        db.session.commit()

        flash("Profile updated successfully.", "success")
        return redirect(url_for("user.profile"))

    return render_template("user/profile.html")

@user.route("/apply-staff", methods=["GET", "POST"])
@login_required
@allowed_roles("TREKKER")
def apply_staff():

    profile = current_user.staff_profile

    if profile and profile.approval_status == "Pending":
        flash("Your application is already pending.", "warning")
        return redirect(url_for("user.dashboard"))

    if profile and profile.approval_status == "Approved":
        flash("You are already an approved staff member.", "info")
        return redirect(url_for("user.dashboard"))

    if request.method == "POST":

        specialization = request.form.get("specialization", "").strip()
        experience_years = request.form.get("experience_years")

        if not experience_years.isdigit():
            flash("enter digit only", "danger")
            return(redirect(url_for("user.apply_staff")))

        if not specialization:
            flash("Please enter your specialization.", "danger")
            return redirect(url_for("user.apply_staff"))
        
        experience_years = int(experience_years)
        
        if experience_years < 0:
            flash("Enter valid experience year", "danger")
            return redirect(url_for("user.apply_staff"))
        
        if len(specialization) > 100:
            flash("Max character for specialization is 100!", "danger")
            return redirect(url_for("user.apply_staff"))

        if profile:
            profile.experience_years = experience_years
            profile.specialization = specialization
            profile.approval_status = "Pending"

        else:
            profile = StaffProfile(
                user_id=current_user.id,
                experience_years=experience_years,
                specialization=specialization,
                approval_status="Pending"
            )
            db.session.add(profile)

        db.session.commit()

        flash("Your staff application has been submitted successfully.", "success")
        return redirect(url_for("user.dashboard"))

    return render_template("user/apply_staff.html", profile=profile)


@user.route("/trending-treks")
@login_required
@allowed_roles("TREKKER", "STAFF")
def trending_treks():

    treks = sorted(
        Trek.query.filter_by(status="Open").all(),
        key=lambda trek: len(trek.bookings),
        reverse=True
    )[:10]

    return render_template("user/trending_treks.html", treks=treks)


@user.route("/staff/<int:staff_id>")
@login_required
@allowed_roles("TREKKER", "STAFF")
def staff_details(staff_id):

    staff = User.query.filter_by(id=staff_id, role="STAFF").first_or_404()

    return render_template("user/staff_details.html", staff=staff)