from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Doctor, Appointment, Treatment, Patient
from datetime import datetime

# Create doctor blueprint
bp = Blueprint('doctor', __name__, url_prefix='/doctor')

# Decorator to restrict access to doctors only
def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'doctor':
            flash('You need doctor privileges to access this page.', 'danger')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@doctor_required
def dashboard():
    # Get doctor profile
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # Get appointment statistics
    total_appointments = Appointment.query.filter_by(doctor_id=doctor.id).count()
    pending_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status='Booked').count()
    completed_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status='Completed').count()
    
    # Get today's appointments
    today = datetime.now().date()
    todays_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        db.func.date(Appointment.appointment_date) == today
    ).all()
    
    return render_template('doctor/dashboard.html',
                         doctor=doctor,
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         completed_appointments=completed_appointments,
                         todays_appointments=todays_appointments)

@bp.route('/appointments')
@login_required
@doctor_required
def appointments():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # Filter by status if provided
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.appointment_date.desc()).all()
    else:
        appointments = Appointment.query.filter_by(doctor_id=doctor.id, status=status_filter).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('doctor/appointments.html', appointments=appointments, status_filter=status_filter)

@bp.route('/appointment/<int:id>')
@login_required
@doctor_required
def appointment_detail(id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    appointment = Appointment.query.get_or_404(id)
    
    # Verify this appointment belongs to this doctor
    if appointment.doctor_id != doctor.id:
        flash('You can only view your own appointments.', 'danger')
        return redirect(url_for('doctor.appointments'))
    
    # Get patient's treatment history
    patient_history = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == appointment.patient_id,
        Appointment.status == 'Completed'
    ).order_by(Treatment.created_at.desc()).all()
    
    return render_template('doctor/appointment_detail.html', 
                         appointment=appointment,
                         patient_history=patient_history)

@bp.route('/appointment/<int:id>/complete', methods=['POST'])
@login_required
@doctor_required
def complete_appointment(id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    appointment = Appointment.query.get_or_404(id)
    
    # Verify this appointment belongs to this doctor
    if appointment.doctor_id != doctor.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('doctor.appointments'))
    
    # Get form data
    diagnosis = request.form.get('diagnosis')
    prescription = request.form.get('prescription')
    notes = request.form.get('notes')
    
    if not diagnosis:
        flash('Diagnosis is required.', 'danger')
        return redirect(url_for('doctor.appointment_detail', id=id))
    
    # Mark appointment as completed
    appointment.status = 'Completed'
    
    # Create treatment record
    treatment = Treatment(
        appointment_id=appointment.id,
        diagnosis=diagnosis,
        prescription=prescription if prescription else '',
        notes=notes if notes else ''
    )
    
    db.session.add(treatment)
    db.session.commit()
    
    flash(f'Appointment marked as completed and treatment recorded.', 'success')
    return redirect(url_for('doctor.appointments'))

@bp.route('/appointment/<int:id>/cancel', methods=['POST'])
@login_required
@doctor_required
def cancel_appointment(id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    appointment = Appointment.query.get_or_404(id)
    
    if appointment.doctor_id != doctor.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('doctor.appointments'))
    
    reason = request.form.get('reason', 'Cancelled by doctor')
    appointment.status = 'Cancelled'
    
    db.session.commit()
    
    flash(f'Appointment cancelled: {reason}', 'info')
    return redirect(url_for('doctor.appointments'))

@bp.route('/availability', methods=['GET', 'POST'])
@login_required
@doctor_required
def availability():
    from app.models import Availability
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        day_of_week = request.form.get('day_of_week')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        
        availability = Availability(
            doctor_id=doctor.id,
            day_of_week=day_of_week,
            start_time=datetime.strptime(start_time, '%H:%M').time() if start_time else None,
            end_time=datetime.strptime(end_time, '%H:%M').time() if end_time else None
        )
        db.session.add(availability)
        db.session.commit()
        
        flash('Availability added successfully!', 'success')
        return redirect(url_for('doctor.availability'))
    
    availabilities = Availability.query.filter_by(doctor_id=doctor.id).all()
    return render_template('doctor/availability.html', availabilities=availabilities)

@bp.route('/availability/delete/<int:id>')
@login_required
@doctor_required
def delete_availability(id):
    from app.models import Availability
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    availability = Availability.query.get_or_404(id)
    
    if availability.doctor_id != doctor.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('doctor.availability'))
    
    db.session.delete(availability)
    db.session.commit()
    
    flash('Availability deleted.', 'success')
    return redirect(url_for('doctor.availability'))

@bp.route('/patients')
@login_required
@doctor_required
def patients():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # Get unique patients who have appointments with this doctor
    patients = db.session.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == doctor.id
    ).distinct().all()
    
    return render_template('doctor/patients.html', patients=patients)
