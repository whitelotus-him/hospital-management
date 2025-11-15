# Hospital Management System (HMS)

## Overview
A web-based Hospital Management System built with Flask that allows Admins, Doctors, and Patients to interact with the system based on their roles.

## Tech Stack
- Flask (Backend)
- Jinja2, HTML, CSS, Bootstrap (Frontend)
- SQLite (Database)
- Flask-Login (Authentication)

## Features

### Admin Dashboard
- Manage doctors and patients (CRUD operations)
- View all appointments
- Search functionality for patients and doctors
- Statistics dashboard

### Doctor Dashboard
- View assigned appointments
- Mark appointments as completed/cancelled
- Add diagnosis and treatment notes
- View patient history

### Patient Dashboard
- Register and login
- Search for doctors by specialization
- Book, reschedule, or cancel appointments
- View appointment history and treatment details

## Project Structure
```
hospital-management-system/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── forms.py
│   ├── utils.py
│   ├── routes/
│   │   ├── home.py
│   │   ├── admin.py
│   │   ├── doctor.py
│   │   └── patient.py
│   ├── templates/
│   │   └── (HTML files)
│   └── static/
│       ├── css/
│       └── js/
├── instance/
├── requirements.txt
├── run.py
├── .gitignore
└── README.md
```


