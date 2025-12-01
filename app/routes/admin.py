# app/routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Admin, Doctor, Patient, Appointment, Specialization
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('home.home'))
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='Booked').count()
    recent_appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         recent_appointments=recent_appointments)

@bp.route('/doctors')
@login_required
@admin_required
def doctors():
    search = request.args.get('search', '')
    if search:
        doctors = Doctor.query.join(Specialization).filter(
            (Doctor.name.contains(search)) |
            (Doctor.phone.contains(search)) |
            (Specialization.name.contains(search))
        ).all()
    else:
        doctors = Doctor.query.all()
    
    return render_template('admin/doctors.html', doctors=doctors, search=search)

@bp.route('/doctor/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_doctor():
    specializations = Specialization.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        specialization_id = request.form.get('specialization')
        experience = request.form.get('experience')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('admin.add_doctor'))
        
        from werkzeug.security import generate_password_hash
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role='doctor'
        )
        db.session.add(new_user)
        db.session.flush()
        
        new_doctor = Doctor(
            user_id=new_user.id,
            name=name,
            phone=phone,
            specialization_id=int(specialization_id),
            experience=int(experience) if experience else 0
        )
        db.session.add(new_doctor)
        db.session.commit()
        
        flash(f'Doctor {name} added successfully!', 'success')
        return redirect(url_for('admin.doctors'))
    
    return render_template('admin/doctor_form.html', doctor=None, specializations=specializations)

@bp.route('/doctor/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    specializations = Specialization.query.all()
    
    if request.method == 'POST':
        doctor.name = request.form.get('name')
        doctor.phone = request.form.get('phone')
        doctor.specialization_id = int(request.form.get('specialization'))
        experience = request.form.get('experience')
        doctor.experience = int(experience) if experience else 0
        
        new_email = request.form.get('email')
        if new_email != doctor.user.email:
            existing = User.query.filter_by(email=new_email).first()
            if existing:
                flash('Email already in use!', 'danger')
                return redirect(url_for('admin.edit_doctor', id=id))
            doctor.user.email = new_email
        
        db.session.commit()
        flash(f'Doctor {doctor.name} updated successfully!', 'success')
        return redirect(url_for('admin.doctors'))
    
    return render_template('admin/doctor_form.html', doctor=doctor, specializations=specializations)

@bp.route('/doctor/delete/<int:id>')
@login_required
@admin_required
def delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    user = doctor.user
    
    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Doctor {doctor.name} deleted successfully!', 'success')
    return redirect(url_for('admin.doctors'))

@bp.route('/patients')
@login_required
@admin_required
def patients():
    search = request.args.get('search', '')
    
    if search:
        patients = Patient.query.join(User).filter(
            (Patient.name.contains(search)) |
            (Patient.phone.contains(search)) |
            (User.email.contains(search))
        ).all()
    else:
        patients = Patient.query.all()
    
    return render_template('admin/patients.html', patients=patients, search=search)

@bp.route('/patient/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_patient():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        date_of_birth = request.form.get('date_of_birth')
        address = request.form.get('address')
        medical_history = request.form.get('medical_history')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('admin.add_patient'))
        
        from werkzeug.security import generate_password_hash
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role='patient'
        )
        db.session.add(new_user)
        db.session.flush()
        
        new_patient = Patient(
            user_id=new_user.id,
            name=name,
            phone=phone,
            date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d').date() if date_of_birth else None,
            address=address,
            medical_history=medical_history
        )
        db.session.add(new_patient)
        db.session.commit()
        
        flash(f'Patient {name} added successfully!', 'success')
        return redirect(url_for('admin.patients'))
    
    return render_template('admin/patient_form.html', patient=None)

@bp.route('/patient/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    
    if request.method == 'POST':
        patient.name = request.form.get('name')
        patient.phone = request.form.get('phone')
        date_of_birth = request.form.get('date_of_birth')
        patient.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date() if date_of_birth else None
        patient.address = request.form.get('address')
        patient.medical_history = request.form.get('medical_history')
        
        new_email = request.form.get('email')
        if new_email != patient.user.email:
            existing = User.query.filter_by(email=new_email).first()
            if existing:
                flash('Email already in use!', 'danger')
                return redirect(url_for('admin.edit_patient', id=id))
            patient.user.email = new_email
        
        db.session.commit()
        flash(f'Patient {patient.name} updated successfully!', 'success')
        return redirect(url_for('admin.patients'))
    
    return render_template('admin/patient_form.html', patient=patient)

@bp.route('/patient/delete/<int:id>')
@login_required
@admin_required
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    user = patient.user
    
    db.session.delete(patient)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Patient {patient.name} deleted successfully!', 'success')
    return redirect(url_for('admin.patients'))

@bp.route('/appointments')
@login_required
@admin_required
def appointments():
    search = request.args.get('search', '')
    
    if search:
        appointments = Appointment.query.join(Patient).join(Doctor).filter(
            (Patient.name.contains(search)) |
            (Doctor.name.contains(search))
        ).all()
    else:
        appointments = Appointment.query.all()
    
    return render_template('admin/appointments.html', appointments=appointments, search=search)
