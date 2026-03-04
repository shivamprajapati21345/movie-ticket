from flask import Flask
from datetime import datetime

def format_datetime_filter(value, format='%d %b %Y, %I:%M %p'):
    """Format a date time to a readable string."""
    if isinstance(value, str):
        dt_object = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt_object.strftime(format)
    if value is None:
        return ""
    return value.strftime(format)

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = 'shivam-booking-secret-key-2024'
    
    app.jinja_env.filters['format_datetime'] = format_datetime_filter
    
    # Register blueprints
    from app.routes import auth_bp, main_bp, movie_bp, booking_bp
    from app.admin_routes import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(movie_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(admin_bp)
    
    return app
