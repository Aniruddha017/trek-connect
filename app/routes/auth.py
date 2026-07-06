from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db 
from app.models import User 

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        mobile_number = request.form['mobile_number'].strip()
        password = request.form['password']

        if not all([name, email, password, mobile_number]):
            flash("All fields are required to be filled!", "danger")
            return redirect(url_for("auth.register"))
        
        if len(mobile_number) < 8:
            flash("Mobile number too short!", "danger")
            return redirect(url_for("auth.register"))
        
        if not mobile_number.isdigit():
            flash("Only numbers allowed in mobile number!", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Enter a longer password", "danger")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter(
            (User.email == email) | (User.mobile_number == mobile_number)
        ).first()


        if existing_user:
            flash("Email or phone number already exists", "danger")
            return redirect(url_for('auth.register'))

        user = User(
            name = name,
            email = email,
            mobile_number = mobile_number,
            password_hash = generate_password_hash(password),
            role="TREKKER"
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful! Please Login", "success")

        return redirect(url_for('auth.login'))
    
    return render_template("auth/register.html")



@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User or Password is not correct", "danger")
            return redirect(url_for("auth.login"))
        
        if user.is_blacklisted:
            flash("User is deactivated!", "danger")
            return redirect(url_for("auth.login"))
        
        if not check_password_hash(user.password_hash, password):
            flash("Incorrect email or password", "danger")
            return redirect(url_for("auth.login"))
        
        login_user(user)

        if user.role == "ADMIN":
            return redirect(url_for("admin.dashboard"))
        elif user.role == "STAFF":
            return redirect(url_for("staff.dashboard")) 
            
        return redirect(
                url_for("user.dashboard")
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