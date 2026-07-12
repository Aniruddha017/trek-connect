from flask import Blueprint, jsonify, abort
from app import db 
from flask_login import login_required, current_user
from app.models import User, Trek, Booking, StaffNotification
from datetime import date
from utils.decorators import allowed_roles


api = Blueprint("api",__name__, url_prefix='/api')


# get a trek's detail 

@api.route("/treks/<int:trek_id>", methods=["GET"])
@login_required
@allowed_roles("ADMIN")
def get_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    return jsonify({
        "id": trek.id,
        "name": trek.name,
        "location": trek.location,
        "difficulty": trek.difficulty,
        "duration_days": trek.duration_days,
        "price": trek.price,
        "total_slots": trek.total_slots,
        "available_slots": trek.available_slots,
        "status": trek.status,
        "start_date": str(trek.start_date),
        "end_date": str(trek.end_date),
        "assigned_staff_count": len(trek.assigned_staff),
        "total_bookings_count": len(trek.bookings)
    }), 200



# get a user's detail

@api.route("/users/<int:user_id>", methods=["GET"])
@login_required
@allowed_roles("ADMIN")
def get_user(user_id):

    user = User.query.get_or_404(user_id)

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "mobile_number": user.mobile_number,
        "role": user.role,
        "is_blacklisted": user.is_blacklisted,
        "total_bookings_count": len(user.bookings)
    }), 200



# cancel booking
@api.route("/bookings/delete/<int:booking_id>", methods=["DELETE"])
@login_required
@allowed_roles("TREKKER", "STAFF")
def cancel_booking_api(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        return jsonify({
            "error": "You are not allowed to cancel this booking."
        }), 403

    trek = Trek.query.get_or_404(booking.trek_id)

    if booking.status != "Booked":
        return jsonify({
            "error": "Only active bookings can be cancelled."
        }), 400

    if trek.start_date <= date.today():
        return jsonify({
            "error": "Cancellation period has ended."
        }), 400

    booking.status = "Cancelled"

    trek.available_slots += 1

    for staff in trek.assigned_staff:
        db.session.add(
            StaffNotification(
                staff_id=staff.id,
                message=f"{current_user.name} cancelled {trek.name}."
            )
        )

    db.session.commit()

    return jsonify({
        "message": "Booking cancelled successfully.",
        "booking_status": "Cancelled"
    }), 200



# get booking details
@api.route("/bookings/<int:booking_id>", methods=["GET"])
@login_required
@allowed_roles("ADMIN")
def get_booking(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    return jsonify({
        "id": booking.id,
        "trek": booking.trek.name,
        "user": booking.user.name,
        "booking_date": str(booking.booking_date),
        "status": booking.status,
        "payment_status": booking.payment_status
    }), 200



# get trek participants
@api.route("/treks/<int:trek_id>/participants", methods=["GET"])
@login_required
@allowed_roles("ADMIN")
def get_trek_participants(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    participants = []

    for booking in trek.bookings:

        participants.append({
            "booking_id": booking.id,
            "user_id": booking.user.id,
            "name": booking.user.name,
            "email": booking.user.email,
            "mobile_number": booking.user.mobile_number,
            "booking_status": booking.status,
            "payment_status": booking.payment_status,
            "booking_date": str(booking.booking_date)   
        })

    return jsonify({
        "trek_id": trek.id,
        "trek_name": trek.name,
        "participant_count": len(participants),
        "participants": participants
    }), 200


# approve a user to staff

@api.route("/staff/<int:user_id>/approve", methods=["POST"])
@login_required
@allowed_roles("ADMIN")
def approve_staff_api(user_id):

    user = User.query.get_or_404(user_id)

    if user.role != "TREKKER":
        return jsonify({
            "error": "Only trekkers can be approved."
        }), 400

    if not user.staff_profile:
        return jsonify({
            "error": "Staff profile not found."
        }), 404

    if user.staff_profile.approval_status == "Approved":
        return jsonify({
            "error": "Already approved."
        }), 400
    
    if user.is_blacklisted:
        return jsonify({
            "error": "Blacklisted users cannot be approved."
        }), 400
    
    if user.staff_profile.approval_status != "Pending":
        return jsonify({
            "error": "Only pending staff applications can be approved."
        }), 400

    user.role = "STAFF"
    user.staff_profile.approval_status = "Approved"

    db.session.commit()

    return jsonify({
        "message": "Staff approved successfully.",
        "user_id": user.id,
        "new_role": user.role 
    }), 200