from flask import Flask

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

# Import routes after app creation to avoid circular imports
from app.routes import home
