from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(email="admin@trek.com").first()

    if not admin:
        admin = User(
            name = "System Admin",
            email = "admin@trek.com",
            password_hash = generate_password_hash("admin@123"),
            mobile_number = "1234567890",
            role = "ADMIN"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin Created Successfully")
        print("Email: admin@trek.com")
        print("Password: admin@123")

    else:

        print("Admin already exists!")