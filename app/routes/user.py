from flask import Blueprint, render_template, redirect, url_for, flash, abort
from app import db
from flask_login import login_required, current_user
from utils.decorators import allowed_roles
from app.models import Trek, User, Booking
from datetime import date


user = Blueprint("user", __name__, url_prefix="/user")


@user.route("/dashboard")
@login_required
@allowed_roles("TREKKER")
def dashboard():

    open_treks = Trek.query.filter_by(status="Open").all()
    bookings = Booking.query.filter_by(user_id=current_user.id).all()

    return render_template("user/dashboard.html", open_treks=open_treks, bookings=bookings)


@user.route("/treks")
@login_required
@allowed_roles("TREKKER")
def treks():
    treks = Trek.query.filter_by(status="Open").all()

    return render_template("user/treks.html", treks=treks)



@user.route("/trek/<int:trek_id>/details")
@login_required
@allowed_roles("TREKKER")
def trek_details(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    return render_template("user/trek_details.html", trek=trek)




@user.route("/treks/<int:trek_id>/book", methods=["POST"])
@login_required
@allowed_roles("TREKKER")
def book_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    existing = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.trek_id == trek.id,
        Booking.status.in_(["Booked", "Completed"])
    ).first()

    if existing:        
        flash("You have already booked this trek!", "warning")
        return redirect(url_for("user.trek_details", trek_id=trek.id))
    
    if trek.status != "Open":
        flash("Trek not open for booking!", "danger")
        return redirect(url_for("user.treks"))


    if trek.available_slots <=0:
        flash("No slots available in this trek.", "warning")
        return redirect(url_for("user.treks"))
    
    if current_user.is_blacklisted == True:
        flash("Blacklisted Users cannot book any trek!", "danger")
        return redirect(url_for("user.treks"))
    
    if trek.start_date <= date.today():
        flash("This trek already started", "danger")
        return redirect(url_for("user.treks"))
    

    booking = Booking(user_id=current_user.id, trek_id=trek.id, status="Booked")
    trek.available_slots -=1
    db.session.add(booking)
    db.session.commit()

    flash("Booking successful!", "success")
    return redirect(url_for("user.bookings"))



@user.route("/bookings")
@login_required
@allowed_roles("TREKKER")
def bookings():
    
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template("user/bookings.html", bookings=bookings)

@user.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
@allowed_roles("TREKKER")
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

    trek.available_slots +=1
    db.session.commit()
    flash("Booking cancelled successfully.","success")
    return redirect(url_for("user.bookings"))



@user.route("/history")
@login_required
@allowed_roles("TREKKER")
def history():
    bookings = Booking.query.filter(Booking.user_id==current_user.id, Booking.status.in_(["Completed", "Cancelled"])).all()

    return render_template("user/history.html", bookings=bookings)

