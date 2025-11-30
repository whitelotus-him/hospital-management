from app import create_app, db
import os

app = create_app()

if __name__ == '__main__':
    # Create instance folder if it doesn't exist
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f'✓ Created instance folder: {instance_path}')
    
    with app.app_context():
        db.create_all()
        print('✓ Database tables created')
    
    print('✓ Starting Hospital Management System...')
    print('✓ Access at: http://localhost:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
