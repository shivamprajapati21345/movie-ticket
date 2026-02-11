from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = 'shivam-booking-secret-key-2024'
    
    # Register blueprints
    from app.routes import auth_bp, main_bp, movie_bp, booking_bp, admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(movie_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(admin_bp)
    
    return app
