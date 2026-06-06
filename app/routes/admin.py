from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Trek
from app import db
from datetime import datetime, timedelta, date
from utils.decorators import allowed_roles
from utils import constants

admin = Blueprint("admin", __name__, url_prefix="/admin")




@admin.route('/dashboard')
@login_required
@allowed_roles("ADMIN")
def dashboard():

    return render_template("admin/dashboard.html")


@admin.route("/treks")
@login_required
@allowed_roles("ADMIN")
def treks():

    treks = Trek.query.all()

    return render_template("admin/treks.html", treks=treks)


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
            end_date = end_date
        )

        db.session.add(trek)
        db.session.commit()

        return redirect(url_for("admin.treks"))
    
    return render_template('admin/create.html')

