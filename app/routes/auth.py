from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db 
from app.models import User 

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        user = User(
            name = request.form['name'],
            email = request.form['email'],
            mobile_number = request.form['mobile_number'],
            password_hash = generate_password_hash(request.form['password']),
            role="TREKKER"
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('auth.login'))
    
    return render_template("auth/register.html")



@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):
            login_user(user)


            if user.role == 'ADMIN':
                return redirect(url_for("admin.dashboard"))
            

            return redirect(
                url_for("auth.dashboard")
            )

    return render_template("auth/login.html")


@auth.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "auth/dashboard.html"
    )


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("auth.login")
    )