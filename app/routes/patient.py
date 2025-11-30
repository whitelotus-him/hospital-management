from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Doctor, Appointment, Patient, Treatment, Availability, Specialization
from app import db
from datetime import datetime, date, time
from functools import wraps

# Create patient blueprint
bp = Blueprint('patient', __name__, url_prefix='/patient')

# Decorator to require patient role
def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'patient':            flash('Access denied. Patients only.', 'danger')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@patient_required
def dashboard():
    # Get patient's appointments statistics
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    total_appointments = Appointment.query.filter_by(patient_id=patient.id).count()
    upcoming_appointments = Appointment.query.filter_by(
        patient_id=patient.id,
        status='Booked'
    ).filter(Appointment.appointment_date >= date.today()).count()
    
    completed_appointments = Appointment.query.filter_by(
        patient_id=patient.id,
        status='Completed'
    ).count()
    
    # Get upcoming appointments
    upcoming = Appointment.query.filter_by(
        patient_id=patient.id,
        status='Booked'
    ).filter(Appointment.appointment_date >= date.today()).order_by(
        Appointment.appointment_date,
        Appointment.appointment_time
    ).limit(5).all()

        # Get all specializations
    from app.models import Specialization
    specializations = Specialization.query.all()
    
    stats = {
        'total': total_appointments,
        'upcoming': upcoming_appointments,
        'completed': completed_appointments
    }
    
    return render_template('patient/dashboard.html', stats=stats, upcoming=upcoming), specializations=specializations

@bp.route('/search-doctors')
@login_required
@patient_required
def search_doctors():
    # Get search parameters
    search_query = request.args.get('search', '')
    specialization = request.args.get('specialization', '')
    
    # Build query
    query = Doctor.query
    
    if search_query:
        query = query.filter(Doctor.name.contains(search_query))
    
    if specialization:
        from app.models import Specialization
        query = query.join(Specialization).filter(Specialization.id == int(specialization))    
    doctors = query.all()
    
    # Get all unique specializations for filter dropdown
    from app.models import Specialization
    ] for s in specializations]
    
    return render_template('patient/search_doctors.html', 
                         doctors=doctors, 
                         specializations=specializations,
                         search_query=search_query,
                         selected_specialization=specialization)

@bp.route('/book-appointment/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@patient_required
def book_appointment(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        appointment_date_str = request.form.get('appointment_date')
        appointment_time_str = request.form.get('appointment_time')
        reason = request.form.get('reason')
        
        try:
            # Parse date and time
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(appointment_time_str, '%H:%M').time()
            
            # Validate date is not in the past
            if appointment_date < date.today():
                flash('Cannot book appointment in the past.', 'danger')
                return redirect(url_for('patient.book_appointment', doctor_id=doctor_id))
            
            # Check if same date and time is already booked with this doctor
            existing = Appointment.query.filter_by(
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status='Booked'
            ).first()
            
            if existing:
                flash('This time slot is already booked. Please choose another time.', 'danger')
                return redirect(url_for('patient.book_appointment', doctor_id=doctor_id))
            
            # Create new appointment
            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason if reason else None,
                status='Booked'
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            flash(f'Appointment booked successfully with Dr. {doctor.name} on {appointment_date.strftime("%d %b %Y")} at {appointment_time.strftime("%I:%M %p")}.', 'success')
            return redirect(url_for('patient.appointments'))
            
        except ValueError as e:
            flash('Invalid date or time format.', 'danger')
            return redirect(url_for('patient.book_appointment', doctor_id=doctor_id))
    
    return render_template('patient/book_appointment.html', doctor=doctor)

@bp.route('/appointments')
@login_required
@patient_required
def appointments():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    # Get filter parameter
    status_filter = request.args.get('status')
    
    query = Appointment.query.filter_by(patient_id=patient.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    appointments = query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).all()
    
    return render_template('patient/appointments.html', appointments=appointments)

@bp.route('/appointment/<int:id>/cancel', methods=['POST'])
@login_required
@patient_required
def cancel_appointment(id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointment = Appointment.query.get_or_404(id)
    
    # Verify this appointment belongs to current patient
    if appointment.patient_id != patient.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('patient.appointments'))
    
    # Only allow cancellation of booked appointments
    if appointment.status != 'Booked':
        flash('Can only cancel booked appointments.', 'warning')
        return redirect(url_for('patient.appointments'))
    
    appointment.status = 'Cancelled'
    db.session.commit()
    
    flash('Appointment cancelled successfully.', 'success')
    return redirect(url_for('patient.appointments'))

@bp.route('/appointment/<int:id>/reschedule', methods=['GET', 'POST'])
@login_required
@patient_required
def reschedule_appointment(id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointment = Appointment.query.get_or_404(id)
    
    # Verify this appointment belongs to current patient
    if appointment.patient_id != patient.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('patient.appointments'))
    
    # Only allow rescheduling of booked appointments
    if appointment.status != 'Booked':
        flash('Can only reschedule booked appointments.', 'warning')
        return redirect(url_for('patient.appointments'))
    
    if request.method == 'POST':
        new_date_str = request.form.get('appointment_date')
        new_time_str = request.form.get('appointment_time')
        
        try:
            new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
            new_time = datetime.strptime(new_time_str, '%H:%M').time()
            
            # Validate date is not in the past
            if new_date < date.today():
                flash('Cannot reschedule to a past date.', 'danger')
                return redirect(url_for('patient.reschedule_appointment', id=id))
            
            # Check if new slot is available
            existing = Appointment.query.filter_by(
                doctor_id=appointment.doctor_id,
                appointment_date=new_date,
                appointment_time=new_time,
                status='Booked'
            ).filter(Appointment.id != id).first()
            
            if existing:
                flash('This time slot is already booked. Please choose another time.', 'danger')
                return redirect(url_for('patient.reschedule_appointment', id=id))
            
            # Update appointment
            appointment.appointment_date = new_date
            appointment.appointment_time = new_time
            db.session.commit()
            
            flash('Appointment rescheduled successfully.', 'success')
            return redirect(url_for('patient.appointments'))
            
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return redirect(url_for('patient.reschedule_appointment', id=id))
    
    return render_template('patient/book_appointment.html', 
                         doctor=appointment.doctor, 
                         appointment=appointment,
                         reschedule=True)

@bp.route('/history')
@login_required
@patient_required
def history():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    # Get all completed appointments with treatments
    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient.id,
        Appointment.status == 'Completed'
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('patient/history.html', treatments=treatments)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
@patient_required
def profile():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        # Update patient information
        contact = request.form.get('contact')
        address = request.form.get('address')
        
        if contact:
            patient.contact = contact
        if address:
            patient.address = address
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('patient.profile'))
    
    return render_template('patient/profile.html', patient=patient)

@bp.route('/doctor/<int:doctor_id>', methods=['GET'])
@login_required
@patient_required
def view_doctor(doctor_id):
    """View doctor profile and available slots"""
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Get doctor availability for next 7 days
    today = date.today()
    week_end = today + timedelta(days=6)
    availabilities = Availability.query.filter_by(doctor_id=doctor_id, is_available=True).filter(
        Availability.date >= today,
        Availability.date <= week_end
    ).order_by(Availability.date, Availability.start_time).all()
    
    return render_template('patient/doctor_profile.html', doctor=doctor, availabilities=availabilities)

@bp.route('/search', methods=['GET', 'POST'])
@login_required
@patient_required
def search_by_specialization():
    """Search doctors by specialization"""
    specializations = Specialization.query.all()
    doctors = []
    selected_spec_id = None
    
    if request.method == 'POST':
        spec_id = request.form.get('specialization_id')
        if spec_id:
            selected_spec_id = int(spec_id)
            doctors = Doctor.query.filter_by(specialization_id=selected_spec_id).all()
    elif request.args.get('spec_id'):
        spec_id = request.args.get('spec_id')
        selected_spec_id = int(spec_id)
        doctors = Doctor.query.filter_by(specialization_id=selected_spec_id).all()
    
    return render_template('patient/search_results.html', 
                         specializations=specializations, 
                         doctors=doctors, 
                         selected_spec_id=selected_spec_id)
