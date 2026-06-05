from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from flask import abort
from app.models import Trek
from app import db
from datetime import datetime


admin = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required():
    if current_user.role != "ADMIN":
        abort(403)



@admin.route('/dashboard')
@login_required
def dashboard():

    admin_required()
    return render_template("admin/dashboard.html")


@admin.route("/treks")
@login_required
def treks():

    admin_required()
    treks = Trek.query.all()

    return render_template("admin/treks.html", treks=treks)


@admin.route("/treks/create", methods=["GET", "POST"])
@login_required
def create_trek():
    if request.method == "POST":

        start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form['end_date'], "%Y-%m-%d").date()
        trek = Trek(
            name = request.form['name'],
            location = request.form['location'],
            difficulty = request.form['difficulty'],
            duration_days = request.form['duration_days'],
            total_slots = request.form['total_slots'],
            available_slots = request.form['total_slots'],
            start_date = start_date,
            end_date = end_date
        )
        db.session.add(trek)
        db.session.commit()

        return redirect(url_for("admin.treks"))
    
    return render_template('admin/create.html')

