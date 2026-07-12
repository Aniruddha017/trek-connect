# Trekking Management Application

A role-based web application built using **Flask** for managing trekking events, staff assignments, and trek bookings. This project was developed as part of the **Modern Application Development I (MAD-I)** course.

The application provides separate dashboards for **Admin**, **Trek Staff**, and **Trekkers**, enabling efficient management of treks, bookings, participants, and staff while preventing overbooking and unauthorized access.

---

## Features

### Admin

- Dashboard with system statistics
- Create, edit and delete treks
- Upload trek images
- Set trek pricing
- View all users, staff, treks and bookings
- Approve or reject staff applications
- Promote trekkers to staff
- Demote staff members
- Blacklist / whitelist users and staff
- Assign staff to treks
- View trek participants
- Search users, staff and treks

---

### Trek Staff

- Secure role-based dashboard
- View assigned treks
- Manage only assigned treks
- Update trek status
- Update available slots
- View registered participants
- Mark treks as completed
- Access restricted from unassigned treks

---

### Trekker

- User registration and login
- Browse available treks
- Search and filter treks
- Book treks
- Cancel bookings before trek starts
- View booking history
- Track booking status
- Update profile information

---

## Security & Validation

- Role-based access control using Flask-Login
- Password hashing
- Route protection
- Backend validation
- Duplicate booking prevention
- Prevent booking when:
  - Trek is full
  - Trek is closed
  - Trek has already started
- Prevent unauthorized staff access
- Confirmation dialogs for critical actions
- Blacklisted users cannot make bookings

---

## Database Schema

The application uses **SQLite** with SQLAlchemy ORM.

### Main Models

- User
- StaffProfile
- Trek
- Booking

### Relationships

- One User → Many Bookings
- One Trek → Many Bookings
- Many Staff ↔ Many Treks
- One User ↔ One Staff Profile

---

## Tech Stack

### Backend

- Flask
- Flask-SQLAlchemy
- Flask-Login
- Werkzeug

### Frontend

- HTML5
- Bootstrap 5
- Jinja2 Templates

### Database

- SQLite

---

## Project Structure

```
project/
│
├── app/
|
│   ├── models.py
|   ├── main_routes.py
│   ├── routes/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── staff.py
│   │   └── user.py
│   ├── templates/
│   └── static/
│
├── utils/
│   ├── constants.py
│   └── decorators.py
│
├── instance/
├── config.py
├── run.py
└── requirements.txt
```

---

## Installation guide for Windows

### Clone the repository

```bash
git clone <link to the repository>
cd <project directory>
```

### Create a virtual environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python run.py
```

The application will start at:

```
http://127.0.0.1:5000/
```

---

## User Roles

| Role | Permissions |
|------|-------------|
| Admin | Full access to system management |
| Trek Staff | Manage assigned treks only |
| Trekker | Browse and book treks |

---

## Core Functionalities

- Role-based authentication
- Trek management
- Booking management
- Staff approval workflow
- Trek assignment system
- Booking history
- Trek status tracking
- Responsive Bootstrap UI

---

## Future Improvements

- Email notifications and app level notification for users
- Improved Charts and analytics dashboard
- Admin audit 
- Multiple trek images
- Trek reviews and ratings
- Staff review
- Map based complete trek view

---

## Course Information

**Course:** Modern Application Development I

The project follows the requirements specified in the MAD-I project statement, including database creation through SQLAlchemy models, role-based authentication, trek booking management, and trekking history tracking.

---

## License

This project was developed for academic purposes as part of the IIT Madras BS Degree Program.