from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Patient
from app.forms import LoginForm, PatientRegisterForm

# Create Blueprint - this groups authentication routes together
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to their dashboard
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    form = LoginForm()
    
    # When form is submitted and valid
    if form.validate_on_submit():
        # Find user by email
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(form.password.data):            # Log the user in
            login_user(user)
            flash('Login successful!', 'success')
            # Redirect to page they were trying to access, or home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home.index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    form = PatientRegisterForm()
    
    if form.validate_on_submit():
        # Create new user account
        hashed_password = generate_password_hash(form.password.data)
        
        # Create User record
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            role='patient'
        )
        db.session.add(new_user)
        db.session.flush()  # Get the user.id without committing
        
        # Create Patient profile
        new_patient = Patient(
            user_id=new_user.id,
            name=form.name.data,
            phone=form.phone.data,
            date_of_birth=form.date_of_birth.data,
            address=form.address.data
        )
        db.session.add(new_patient)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required  # User must be logged in to logout
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home.index'))
