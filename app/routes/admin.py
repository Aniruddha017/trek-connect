from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Trek, User, StaffProfile, Booking, StaffNotification
from app import db
from datetime import datetime, timedelta, date
from utils.decorators import allowed_roles
from utils import constants
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os
import uuid
from sqlalchemy import or_
admin = Blueprint("admin", __name__, url_prefix="/admin")


def trek_is_locked(trek):
    return trek.status == "Completed"



@admin.route("/dashboard")
@login_required
@allowed_roles("ADMIN")
def dashboard():

    total_users = User.query.count()
    total_staff = (User.query.join(StaffProfile).filter(
        User.role == "STAFF",
        StaffProfile.approval_status == "Approved"
        ).count())
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
        price = float(request.form['price'])

        filename = None

        if image and image.filename:

            filename = (f"{uuid.uuid4().hex}_"f"{secure_filename(image.filename)}")
            
            extension = filename.rsplit(".", 1)[1].lower()

            if extension not in ["jpg", "jpeg", "png"]:
                flash("Only JPG and PNG images are allowed.", "danger")
                return redirect(url_for("admin.create_trek"))


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
        
        if price < 0:
            flash("Price cannot be negative.", "danger")
            return redirect(request.url)

        trek = Trek(
            name = name,
            location = location,
            difficulty = difficulty,
            duration_days = duration_days,
            total_slots = total_slots,
            available_slots = available_slots,
            start_date = start_date,
            end_date = end_date,
            price=price,
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
                        
            extension = filename.rsplit(".", 1)[1].lower()
            if extension not in ["jpg", "jpeg", "png"]:
                flash("Only JPG and PNG images are allowed.", "danger")
                return redirect(url_for("admin.edit_trek", trek_id=trek.id))

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
        price = float(request.form["price"])

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
        
        if price < 0:
            flash("Price cannot be negative.", "danger")
            return redirect(request.url)


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
        trek.price = price

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
    
    search = request.args.get("search", "").strip()
    
    query = User.query
    
    if search:
        query = query.filter(or_(User.name.ilike(f"%{search}%"),
                                 User.email.ilike(f"%{search}%"),
                                 User.mobile_number.ilike(f"%{search}%")))
    
    users = query.order_by(User.name).all()

    return render_template("admin/users.html", users=users, constants=constants)


@admin.route("/staff")
@login_required
@allowed_roles("ADMIN")
def staff():
    search = request.args.get("search", "").strip()
    query = User.query.join(StaffProfile).filter(User.role=="STAFF", StaffProfile.approval_status == "Approved")
    
    if search:
        query = query.filter(or_(User.name.ilike(f"%{search}%"),
                                 User.email.ilike(f"%{search}%")))

    staff_members = query.order_by(User.name).all()

    pending_requests = StaffProfile.query.filter_by(approval_status="Pending").count()

    
    return render_template("admin/staff.html", staff_members=staff_members, pending_requests=pending_requests)


@admin.route("/staff/requests")
@login_required
@allowed_roles("ADMIN")
def staff_requests():

    search = request.args.get("search", "").strip()

    query = (User.query.join(StaffProfile).filter(
        User.role == "TREKKER",
        StaffProfile.approval_status == "Pending"))

    if search:
        query = query.filter(or_(
            User.name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.mobile_number.ilike(f"%{search}%")
        ))
    
    pending_staff = query.order_by(User.name).all()

    return render_template("admin/staff_requests.html", pending_staff=pending_staff)


@admin.route("/staff/<int:user_id>/approve", methods=["POST"])
@login_required
@allowed_roles("ADMIN")
def approve_staff(user_id):

    user = User.query.get_or_404(user_id)

    if user.role != "TREKKER":
        flash("Only trekkers' staff requests can be approved.", "danger")
        return redirect(url_for("admin.staff_requests"))

    if not user.staff_profile:
        flash("Staff profile not found.", "danger")
        return redirect(url_for("admin.staff_requests"))

    if user.staff_profile.approval_status == "Approved":
        flash("Staff member is already approved.", "warning")
        return redirect(url_for("admin.staff_requests"))

    user.role = "STAFF"
    user.staff_profile.approval_status = "Approved"
    db.session.commit()

    flash(f"{user.name} has been approved as Trek Staff.", "success")

    return redirect(url_for("admin.staff_requests"))

@admin.route("/staff/<int:user_id>/reject", methods=["POST"])
@login_required
@allowed_roles("ADMIN")
def reject_staff(user_id):

    user = User.query.get_or_404(user_id)

    if user.role != "TREKKER":
        flash("Only trekkers' requests can be rejected.", "danger")
        return redirect(url_for("admin.staff_requests"))

    if not user.staff_profile:
        flash("Staff profile not found.", "danger")
        return redirect(url_for("admin.staff_requests"))

    if user.staff_profile.approval_status == "Rejected":

        flash("Staff request has already been rejected.", "warning")
        return redirect(url_for("admin.staff_requests"))

    user.staff_profile.approval_status = "Rejected"
    db.session.commit()

    flash(f"{user.name}'s staff request has been rejected.", "success")

    return redirect(url_for("admin.staff_requests"))

@admin.route("/users/promote/<int:user_id>", methods=["POST"])
@login_required
@allowed_roles("ADMIN")
def apply_for_staff(user_id):
    
    user = User.query.get_or_404(user_id)

    if user.role == "ADMIN":
        flash("Admin cannot be promoted", "danger")
        return redirect(url_for("admin.users"))
    
    if user.role == "STAFF":
        flash("User is already a staff member.", "warning")
        return redirect(url_for("admin.users"))
    
    if user.is_blacklisted:
        flash("User is blacklisted, cannot apply for staff!", "warning")
        return redirect(url_for("admin.users"))
    
    if (user.staff_profile and user.staff_profile.approval_status == "Pending"):
        flash("Staff request is already pending.", "warning")
        return redirect(url_for("admin.users"))

    if not user.staff_profile:
        profile = StaffProfile(user_id=user.id, approval_status="Pending")
        db.session.add(profile)
    else:
        user.staff_profile.approval_status = "Pending"
    
    db.session.commit()
    flash("Staff request added successfully.","success")
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
    
    if user.staff_profile:
        user.staff_profile.approval_status = "Rejected"
    
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

        old_staff = list(trek.assigned_staff)

        trek.assigned_staff.clear()

        for staff_id in selected_staff_ids:

            staff = User.query.get_or_404(staff_id)
            if staff.role != "STAFF":
                continue
            trek.assigned_staff.append(staff)

        all_staff = set(old_staff + trek.assigned_staff)

        for staff in all_staff:
            db.session.add(
                StaffNotification(staff_id=staff.id,
                                  message=f"Assignment for '{trek.name}' has been updated by the administrator. Please check if you were removed or new staff was added")
            )

        db.session.commit()

        flash("Staff assignments updated!", "success")

        return redirect(url_for("admin.treks"))
    

    staff_members = (User.query.join(StaffProfile).filter(
        User.role == "STAFF",
        User.is_blacklisted == False,
        StaffProfile.approval_status == "Approved"
        ).all())
    
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

    search = request.args.get("search", "").strip()
    query = Booking.query.join(User).join(Trek)

    if search:
        query = query.filter(or_(
            User.name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            Trek.name.ilike(f"%{search}%")
        ))

    bookings = query.order_by(Booking.booking_date.desc()).all()

    return render_template("admin/bookings.html",bookings=bookings)


@admin.route("/profile", methods=["GET", "POST"])
@login_required
@allowed_roles("ADMIN")
def profile():

    if request.method == "POST":

        name = request.form["name"].strip()
        mobile_number = request.form["mobile_number"].strip()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not name:
            flash("Name cannot be empty.", "danger")
            return redirect(url_for("admin.profile"))

        if not mobile_number:
            flash("Mobile number is required.", "danger")
            return redirect(url_for("admin.profile"))

        if not mobile_number.isdigit():
            flash("Only numbers allowed in mobile number.", "danger")
            return redirect(url_for("admin.profile"))

        if len(mobile_number) < 8:
            flash("Mobile number is too short.", "danger")
            return redirect(url_for("admin.profile"))

        existing_user = User.query.filter(
            User.mobile_number == mobile_number,
            User.id != current_user.id
        ).first()

        if existing_user:
            flash("Mobile number already exists.", "danger")
            return redirect(url_for("admin.profile"))

        current_user.name = name
        current_user.mobile_number = mobile_number

        if password:

            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return redirect(url_for("admin.profile"))

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return redirect(url_for("admin.profile"))

            current_user.password_hash = generate_password_hash(password)

        db.session.commit()

        flash("Profile updated successfully.", "success")
        return redirect(url_for("admin.profile"))

    return render_template("admin/profile.html")