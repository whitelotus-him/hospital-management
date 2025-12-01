seed.py# seed.py - Creates the default admin user
from app import create_app, db
from app.models import User, Admin
from werkzeug.security import generate_password_hash

# Create Flask app context
app = create_app()

with app.app_context():
    # Check if admin already exists
    admin_user = User.query.filter_by(email='admin@hospital.com').first()
    
    if not admin_user:
        print('Creating admin user...')
        
        # Create admin User account
        admin_user = User(
            email='admin@hospital.com',
                        role='admin'
        )
        db.session.add(admin_user)
            admin_user.set_password('admin123')
        db.session.flush()  # Get the user ID
        
        # Create Admin profile
        admin_profile = Admin(
            user_id=admin_user.id,
            name='System Administrator'
        )
        db.session.add(admin_profile)
        db.session.commit()
        
        print('Admin user created successfully!')
        print('Email: admin@hospital.com')
        print('Password: admin123')
    else:
        print('Admin user already exists.')
