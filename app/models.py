from datetime import datetime, UTC
from app import db
from flask_login import UserMixin

trek_staff = db.Table(
    "trek_staff", 
    db.Column("trek_id", db.Integer, db.ForeignKey("treks.id"), primary_key=True),
    db.Column("staff_id", db.Integer, db.ForeignKey("users.id"), primary_key=True)   
)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    bookings = db.relationship("Booking", backref="user", lazy=True)
    staff_profile = db.relationship("StaffProfile", backref="user", uselist=False)
    assigned_treks = db.relationship("Trek", secondary=trek_staff, back_populates="assigned_staff")



class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    experience_years = db.Column(db.Integer, default=0)
    specialization = db.Column(db.String(100))


class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    assigned_staff = db.relationship("User", secondary=trek_staff, back_populates="assigned_treks")
    time_added = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    bookings = db.relationship("Booking", backref="trek", lazy=True)

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    status = db.Column(db.String(20), default="Booked")
    payment_status = db.Column(db.String(20), default="Pending")

    __table_args__ = (db.UniqueConstraint("user_id", "trek_id", name="unique_user_trek_booking"),)

