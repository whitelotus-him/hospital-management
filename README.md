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

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/whitelotus-him/hospital-management.git
   cd hospital-management
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python
   >>> from app import create_app, db
   >>> app = create_app()
   >>> with app.app_context():
   >>>     db.create_all()
   >>> exit()
   ```

5. **Generate seed data (optional)**
   ```bash
   python seed.py
   ```
   This creates:
   - Admin user: `admin@hospital.com` / `admin123`
   - 5 sample doctors
   - 10 sample patients

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   - Open browser and go to: `http://localhost:5000`

## Default Credentials

After running `seed.py`, use these credentials:

- **Admin**: admin@hospital.com / admin123
- **Doctor**: doctor1@hospital.com / doctor123
- **Patient**: patient1@hospital.com / patient123

## Database Schema

The system uses 8 database models:

1. **User** - Base user authentication (email, password, role)
2. **Admin** - Admin profile (linked to User)
3. **Doctor** - Doctor profile (name, specialization, availability)
4. **Patient** - Patient profile (name, contact, address)
5. **Appointment** - Appointment bookings (date, time, status)
6. **Treatment** - Treatment records (diagnosis, treatment notes)
7. **Availability** - Doctor availability slots
8. **Specialization** - Medical specializations

## Key Features

### Security
- Password hashing using Werkzeug
- Flask-Login session management
- Role-based access control
- CSRF protection

### Validation
- Double-booking prevention
- Date/time validation
- Form validation (WTForms)
- Input sanitization

### User Experience
- Responsive Bootstrap design
- Flash messages for user feedback
- Role-based navigation
- Search functionality

## Testing

To test the application:

1. Register as a patient or use seed data
2. Log in with appropriate credentials
3. Test each role's features:
   - **Admin**: Manage doctors, view appointments
   - **Doctor**: View appointments, add treatments
   - **Patient**: Search doctors, book appointments

## Troubleshooting

**Database not found error:**
```bash
# Delete the old database and recreate
rm instance/hospital.db
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

**Port already in use:**
```bash
# Change port in run.py or kill the process using port 5000
```

## Project Timeline

- **Day 1-2**: Database models, authentication
- **Day 3**: Admin dashboard
- **Day 4**: Doctor dashboard
- **Day 5**: Patient dashboard
- **Day 6-7**: UI/UX improvements, bug fixes
- **Day 8-9**: Testing, documentation
- **Day 10**: Final delivery

## Technologies Used

- **Backend**: Flask 2.3.0, SQLAlchemy, Flask-Login
- **Frontend**: Jinja2, HTML5, CSS3, Bootstrap 5
- **Database**: SQLite3
- **Forms**: Flask-WTF, WTForms
- **Security**: Werkzeug password hashing

## License

This project is created for educational purposes.

## Author

Developed as part of Application Development I course project.


