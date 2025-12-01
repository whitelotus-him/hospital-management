from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Doctor, Availability, User
from datetime import datetime, timedelta
from functools import wraps

bp = Blueprint('availability', __name__, url_prefix='/doctor')

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'doctor':
            flash('Access denied', 'danger')
            return redirect(url_for('home.home'))
    return decorated_function

@bp.route('/availability', methods=['GET', 'POST'])
@login_required
@doctor_required
def manage_availability():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found', 'danger')
        return redirect(url_for('home.index'))
    
    if request.method == 'POST':
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            # Check if date is within next 7 days
            today = datetime.now().date()
            if date_obj < today or date_obj > today + timedelta(days=6):
                flash('Please select a date within the next 7 days', 'danger')
                return redirect(url_for('availability.manage_availability'))
            
            # Check if slot already exists
            existing = Availability.query.filter_by(
                doctor_id=doctor.id,
                date=date_obj,
                start_time=start_time,
                end_time=end_time
            ).first()
            
            if existing:
                flash('This slot already exists', 'warning')
                return redirect(url_for('availability.manage_availability'))
            
            availability = Availability(
                doctor_id=doctor.id,
                date=date_obj,
                start_time=start_time,
                end_time=end_time,
                is_available=True
            )
            db.session.add(availability)
            db.session.commit()
            flash('Availability slot added successfully', 'success')
        except ValueError:
            flash('Invalid date or time format', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Error adding availability slot', 'danger')
        
        return redirect(url_for('availability.manage_availability'))
    
    # Get availability for next 7 days
    today = datetime.now().date()
    week_end = today + timedelta(days=6)
    availabilities = Availability.query.filter_by(doctor_id=doctor.id).filter(
        Availability.date >= today,
        Availability.date <= week_end
    ).order_by(Availability.date, Availability.start_time).all()
    
    return render_template('doctor/availability.html', availabilities=availabilities, doctor=doctor)

@bp.route('/availability/<int:id>/delete', methods=['POST'])
@login_required
@doctor_required
def delete_availability(id):
    availability = Availability.query.get_or_404(id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if availability.doctor_id != doctor.id:
        flash('Access denied', 'danger')
        return redirect(url_for('home.index'))
    
    try:
        db.session.delete(availability)
        db.session.commit()
        flash('Availability slot deleted', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting availability slot', 'danger')
    
    return redirect(url_for('availability.manage_availability'))
