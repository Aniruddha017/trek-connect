from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Trek, User, StaffProfile, Booking
from app import db
from datetime import datetime, timedelta, date
from utils.decorators import allowed_roles
from utils import constants
from werkzeug.utils import secure_filename
import os
import uuid
from sqlalchemy import or_
admin = Blueprint("admin", __name__, url_prefix="/admin")


def trek_is_locked(trek):
    return trek.status == "Completed"


from app.models import Trek, User, Booking

@admin.route("/dashboard")
@login_required
@allowed_roles("ADMIN")
def dashboard():

    total_users = User.query.count()
    total_staff = User.query.filter_by(role="STAFF").count()
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()
    recent_bookings = (Booking.query.order_by(Booking.booking_date.desc()).limit(5).all())


    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings,
        recent_bookings=recent_bookings
    )


@admin.route("/treks")
@login_required
@allowed_roles("ADMIN")
def treks():

    treks = Trek.query.all()
    
    search = request.args.get("search", "").strip()
    
    query = Trek.query
    if search != "":
        query = query.filter(or_(Trek.name.ilike(f"%{search}%"), 
                                 Trek.location.ilike(f"%{search}%"),
                                 Trek.difficulty.ilike(f"%{search}%")))
    
    treks = query.order_by(Trek.start_date).all()


    return render_template("admin/treks.html", treks=treks, constants = constants)


@admin.route("/treks/create", methods=["GET", "POST"])
@login_required
@allowed_roles("ADMIN")
def create_trek():

    if request.method == "POST":

        name = request.form['name'].strip()
        location = request.form['location'].strip()
        difficulty = request.form['difficulty']
        duration_days = int(request.form['duration_days'])
        total_slots = int(request.form['total_slots'])
        available_slots = total_slots
        start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d").date()
        end_date = start_date + timedelta(days=(duration_days -1))
        image = request.files.get("image")

        filename = None

        if image and image.filename:

            filename = (f"{uuid.uuid4().hex}_"f"{secure_filename(image.filename)}")
            image.save(os.path.join("app/static/uploads/trek_images", filename))
        


        existing_trek = Trek.query.filter_by(name=name).first()

        if existing_trek:
            flash("Trek name already exists, choose a unique name!", "danger")
            return redirect(url_for("admin.create_trek"))
        
        if duration_days <=0:
            flash("duration should be greater than 0", "danger")
            return redirect(url_for("admin.create_trek"))
        
        if total_slots <=0:
            flash("slots should be greater than 0", "danger")
            return redirect(url_for("admin.create_trek"))
        
        if difficulty not in constants.TREK_DIFFICULTIES:
            flash("Invalid difficulty entered", "danger")
            return redirect(url_for("admin.create_trek"))
        
        if start_date < date.today():
            flash("start date cannot be in past!", "danger")
            return redirect(url_for("admin.create_trek"))

        trek = Trek(
            name = name,
            location = location,
            difficulty = difficulty,
            duration_days = duration_days,
            total_slots = total_slots,
            available_slots = available_slots,
            start_date = start_date,
            end_date = end_date,
            image_filename = filename
        )

        db.session.add(trek)
        db.session.commit()

        return redirect(url_for("admin.treks"))
    
    return render_template('admin/create.html', difficulties = constants.TREK_DIFFICULTIES)


@admin.route("/treks/edit/<int:trek_id>", methods=["GET", "POST"])
@login_required
@allowed_roles("ADMIN")
def edit_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)
    
    if trek_is_locked(trek):
        flash("Completed Trek cannot be edited!", "danger")
        return redirect(url_for("admin.treks"))
    
    if request.method == "POST":
        
        filename = trek.image_filename

        image = request.files.get("image")

        if image and image.filename:

            filename = (f"{uuid.uuid4().hex}_"f"{secure_filename(image.filename)}")
            image.save(os.path.join("app/static/uploads/trek_images", filename))

        trek.image_filename = filename

        name = request.form['name'].strip()
        location = request.form['location'].strip()
        difficulty = request.form['difficulty']
        duration_days = int(request.form['duration_days'])
        description = request.form["description"]
        total_slots = int(request.form['total_slots'])
        start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d").date()
        end_date = start_date + timedelta(days=(duration_days -1))
        status = request.form["status"]

        booked_slots = trek.total_slots - trek.available_slots

        existing_trek = Trek.query.filter(Trek.name==name, Trek.id!=trek.id).first()

        if existing_trek:
            flash("Trek name already exists, choose a unique name!", "danger")
            return redirect(url_for("admin.edit_trek", trek_id=trek.id))
        
        if duration_days <=0:
            flash("duration should be greater than 0", "danger")
            return redirect(url_for("admin.edit_trek", trek_id=trek.id))
        
        if total_slots <=0:
            flash("slots should be greater than 0", "danger")
            return redirect(url_for("admin.edit_trek", trek_id=trek.id))
        
        if total_slots < booked_slots:
            flash(f"Total slots cannot be less than already booked slots(current bookings: {booked_slots})", "danger")
            return redirect(url_for("admin.edit_trek", trek_id=trek.id))
        
        if difficulty not in constants.TREK_DIFFICULTIES:
            flash("Invalid difficulty entered", "danger")
            return redirect(url_for("admin.edit_trek", trek_id=trek.id))
        
        if status not in constants.TREK_STATUSES:
            flash("Invalid trek status", "danger")
            return redirect(url_for("admin.edit_trek", trek_id=trek.id))


        trek.name = name
        trek.location = location
        trek.difficulty = difficulty
        trek.duration_days = duration_days
        trek.description = description
        trek.total_slots = total_slots
        trek.available_slots = total_slots - booked_slots
        trek.start_date = start_date
        trek.end_date = end_date
        trek.status = status

        db.session.commit()

        flash("Trek details updated successfully", "success")

        return redirect(url_for("admin.treks"))
    
    return render_template("admin/edit_trek.html", trek=trek, difficulties=constants.TREK_DIFFICULTIES, statuses=constants.TREK_STATUSES)


@admin.route("/treks/delete/<int:trek_id>", methods=["POST"])
@login_required
@allowed_roles("ADMIN")
def delete_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    if trek_is_locked(trek):
        flash("Completed Trek cannot be deleted", "danger")
        return redirect(url_for("admin.treks"))
    
    
    if trek.status != "Pending":
        flash(
            "Only pending treks can be deleted",
            "danger"
        )
        return redirect(url_for("admin.treks"))

    if trek.bookings:
        flash(
            "Cannot delete trek with existing bookings",
            "danger"
        )
        return redirect(url_for("admin.treks"))
    
    db.session.delete(trek)
    db.session.commit()

    flash("Trek deleted successfully", "success")

    return redirect(url_for("admin.treks"))

@admin.route("/users")
@login_required
@allowed_roles("ADMIN")
def users():

    users = User.query.order_by(User.name).all()

    return render_template("admin/users.html", users=users)


@admin.route("/staff")
@login_required
@allowed_roles("ADMIN")
def staff():

    staff_members = User.query.filter_by(role="STAFF").all()
    
    return render_template("admin/staff.html", staff_members=staff_members)



@admin.route("/users/promote/<int:user_id>", methods=["POST"])
@login_required
@allowed_roles("ADMIN")
def promote_to_staff(user_id):
    
    user = User.query.get_or_404(user_id)

    if user.role == "ADMIN":
        flash("Admin cannot be promoted", "danger")
        return redirect(url_for("admin.users"))
    
    user.role="STAFF"

    if not user.staff_profile:
        profile = StaffProfile(user_id=user.id)
        db.session.add(profile)
    
    db.session.commit()
    return redirect(url_for("admin.users"))

@admin.route("/users/demote/<int:user_id>", methods=["POST"])
@login_required
@allowed_roles("ADMIN")
def demote_to_user(user_id):

    user = User.query.get_or_404(user_id)
    if user.role == "ADMIN":
        flash("Admin cannot be demoted", "danger")
        return redirect(url_for("admin.users"))
    
    active_treks = []
    for trek in user.assigned_treks:
        if trek.status != "Completed":
            active_treks.append(trek)

    if active_treks:
        flash("Staff assigned to some trek, cannot demote until all treks assigned are completed!", "danger")
        return redirect(url_for("admin.users"))

    user.role = "TREKKER"
    db.session.commit()
    return redirect(url_for("admin.users"))


@admin.route("/users/blacklist/<int:user_id>", methods=["POST"])
@login_required
@allowed_roles("ADMIN")
def blacklist_user(user_id):

    user = User.query.get_or_404(user_id)
    
    active_treks = []
    for trek in user.assigned_treks:
        if trek.status != "Completed":
            active_treks.append(trek)
    
    if active_treks:
        flash("Staff assigned to some trek, clear assignment first", "danger")
        return redirect(url_for("admin.users"))

    if user.role == "ADMIN":
        flash("Admin cannot be blacklisted!", "danger")
        return redirect(url_for("admin.users"))
    
    user.is_blacklisted = True
    db.session.commit()
    return redirect(url_for("admin.users"))

@admin.route("/users/whitelist/<int:user_id>", methods=["POST"])
@login_required
@allowed_roles("ADMIN")
def whitelist_user(user_id):

    user = User.query.get_or_404(user_id)
    user.is_blacklisted = False
    db.session.commit()
    return redirect(url_for("admin.users"))

@admin.route("/trek/<int:trek_id>/assign", methods=["GET", "POST"])
@login_required
@allowed_roles("ADMIN")
def assign_staff_to_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    if trek_is_locked(trek):
        flash("Edit not allowed for completed treks", "danger")
        return redirect(url_for("admin.treks"))
    

    if request.method == "POST":

        selected_staff_ids = set(map(int, request.form.getlist("staff_ids")))

        trek.assigned_staff.clear()

        for staff_id in selected_staff_ids:

            staff = User.query.get_or_404(staff_id)
            if staff.role != "STAFF":
                continue
            trek.assigned_staff.append(staff)

        db.session.commit()

        flash("Staff assignments updated!", "success")

        return redirect(url_for("admin.treks"))

    staff_members = User.query.filter_by(role="STAFF", is_blacklisted=False).all()

    return render_template("admin/assign_staff.html", trek=trek, staff_members=staff_members)

@admin.route("/treks/<int:trek_id>/participants")
@login_required
@allowed_roles("ADMIN")
def trek_participants(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    return render_template("admin/participants.html",trek=trek)

@admin.route("/bookings")
@login_required
@allowed_roles("ADMIN")
def bookings():

    bookings = Booking.query.all()

    return render_template("admin/bookings.html",bookings=bookings)
