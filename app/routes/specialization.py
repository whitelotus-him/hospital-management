from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.models import Specialization, db

bp = Blueprint('specialization', __name__, url_prefix='/admin')

# Admin-only decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('home.home'))
        return f(*args, **kwargs)
    return decorated_function

# List all specializations
@bp.route('/specializations')
@login_required
@admin_required
def specializations():
    specs = Specialization.query.all()
    return render_template('admin/specializations.html', specializations=specs)

# Add new specialization
@bp.route('/specialization/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_specialization():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Specialization name is required', 'danger')
            return redirect(url_for('specialization.add_specialization'))
        
        existing = Specialization.query.filter_by(name=name).first()
        if existing:
            flash('Specialization already exists', 'danger')
            return redirect(url_for('specialization.add_specialization'))
        
        spec = Specialization(name=name, description=description)
        db.session.add(spec)
        db.session.commit()
        flash(f'Specialization "{name}" added successfully!', 'success')
        return redirect(url_for('specialization.specializations'))
    
    return render_template('admin/specialization_form.html', specialization=None)

# Edit specialization
@bp.route('/specialization/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_specialization(id):
    spec = Specialization.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Specialization name is required', 'danger')
            return redirect(url_for('specialization.edit_specialization', id=id))
        
        existing = Specialization.query.filter_by(name=name).filter(Specialization.id != id).first()
        if existing:
            flash('Specialization name already exists', 'danger')
            return redirect(url_for('specialization.edit_specialization', id=id))
        
        spec.name = name
        spec.description = description
        db.session.commit()
        flash(f'Specialization "{name}" updated successfully!', 'success')
        return redirect(url_for('specialization.specializations'))
    
    return render_template('admin/specialization_form.html', specialization=spec)

# Delete specialization
@bp.route('/specialization/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_specialization(id):
    spec = Specialization.query.get_or_404(id)
    
    if spec.doctors:
        flash('Cannot delete specialization with associated doctors', 'danger')
        return redirect(url_for('specialization.specializations'))
    
    name = spec.name
    db.session.delete(spec)
    db.session.commit()
    flash(f'Specialization "{name}" deleted successfully!', 'success')
    return redirect(url_for('specialization.specializations'))
