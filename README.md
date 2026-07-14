# Trekking Management Application

A role-based web application built using **Flask** for managing trekking events, staff assignments, and trek bookings. 

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
- StaffNotification

### Relationships

- One User → Many Bookings
- One Trek → Many Bookings
- Many Staff ↔ Many Treks
- One User ↔ One Staff Profile
- One User → Many Staff Notifications

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
- Chart.js

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
|   |   ├── api.py
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
├── __init_db__.py
├── api.yaml
└── requirements.txt
```

---

### Static Uploads

Uploaded files are stored in:

- `app/static/uploads/profile_images`
- `app/static/uploads/trek_images`

If the upload directories do not exist, create them before running the application:

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

### Initialize the Database

Run the following command to create the database and the default administrator account:

```bash
python __init_db__.py
```

This creates:

- SQLite database (`trek.db`)
- Default administrator account

**Admin Credentials**

Email:
```
admin@trek.com
```

Password:
```
admin@123
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
- REST APIs with JSON responses for limited operations
- Analytics dashboards using Chart.js

---

## API Documentation

The REST API specification is provided separately in the accompanying YAML file.

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

## Image Credits

Images used in the landing page and sample trek images are sourced from publicly available websites for educational and demonstration purposes only.

All trademarks, photographs, and other media remain the property of their respective owners.


## License

This project was developed for academic purposes as part of the IIT Madras BS Degree Program.