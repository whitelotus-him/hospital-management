# Quick Start Guide

## Hospital Management System

### Step 1: Clone & Setup

```bash
git clone https://github.com/whitelotus-him/hospital-management.git
cd hospital-management
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Initialize Database

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
...     exit()
```

### Step 3: Load Sample Data

```bash
python seed.py
```

### Step 4: Run Application

```bash
python run.py
```

App runs at: **http://localhost:5000**

### Step 5: Login with Sample Accounts

- **Admin**: admin@hospital.com / admin123
- **Doctor**: doctor1@hospital.com / doctor123
- **Patient**: patient1@hospital.com / patient123

## Features

✓ Admin: Manage doctors and patients
✓ Doctor: View appointments and add treatments
✓ Patient: Search doctors and book appointments
✓ Secure authentication and role-based access
✓ Responsive Bootstrap UI

## File Structure

```
app/
├── __init__.py          # CSRF protection & config
├── models.py            # 8 database models
├── forms.py             # WTForms validation
├── routes/              # 8 route files
├── templates/           # Jinja2 templates
└── static/              # CSS & JavaScript
```

For detailed info, see **README.md**
