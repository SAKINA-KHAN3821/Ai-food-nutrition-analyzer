"""
AI-Based Nutrition Analyzer using Food Image Recognition
Main Flask Application

Student: Sakina Khan
College: Tilak College of Science and Commerce
Course: TYBSc CS
"""

from flask import Flask, render_template, session, request, abort
from backend.models import db
from backend.routes import api, pages, init_food_recognizer
from config import config
import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Add Stripe import conditionally
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    stripe = None
    STRIPE_AVAILABLE = False

def create_app(config_name='development'):
    """
    Application factory
    
    Args:
        config_name: Configuration environment ('development', 'testing', 'production')
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__, 
                template_folder='frontend/templates',
                static_folder='frontend/static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    stripe_enabled = False
    if STRIPE_AVAILABLE:
        stripe_secret = os.environ.get('STRIPE_SECRET_KEY')
        stripe_publishable = os.environ.get('STRIPE_PUBLISHABLE_KEY')
        # Enable Stripe if both keys are present (even if they're test/dummy keys)
        if stripe_secret and stripe_publishable:
            app.config['STRIPE_SECRET_KEY'] = stripe_secret
            app.config['STRIPE_PUBLISHABLE_KEY'] = stripe_publishable
            stripe.api_key = stripe_secret
            stripe_enabled = True
        else:
            print("Warning: STRIPE_SECRET_KEY or STRIPE_PUBLISHABLE_KEY not set. Payment features disabled.")
    else:
        print("Warning: Stripe not installed. Payment features disabled.")
    app.config['STRIPE_ENABLED'] = stripe_enabled
    
    # Create required directories
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(api)
    app.register_blueprint(pages)
    if stripe_enabled:
        # Add payment blueprint
        from backend.payment import payment_bp
        app.register_blueprint(payment_bp, url_prefix='/payment')
    
    # Initialize database
    with app.app_context():
        db.create_all()
        # Do not initialize heavy AI model at app startup to avoid unnecessary imports/network checks.
        # The recognizer will be initialized lazily when needed (e.g., during /api/food/recognize).

    @app.before_request
    def validate_form_csrf():
        """CSRF check for form-based endpoints only."""
        if request.method == 'POST' and request.path in {'/login', '/register', '/logout'}:
            form_token = request.form.get('csrf_token', '')
            session_token = session.get('csrf_token', '')
            if not form_token or not session_token or form_token != session_token:
                abort(400)
        if (
            request.path == '/payment/create-intent'
            and request.method == 'POST'
            and 'user_id' in session
        ):
            header_token = request.headers.get('X-CSRF-Token', '')
            session_token = session.get('csrf_token', '')
            if not header_token or not session_token or header_token != session_token:
                abort(400)
        # Note: JSON API endpoints are protected by browser same-site cookies and the login_required decorator.
        # Do not enforce CSRF tokens for /api/ endpoints to avoid breaking mobile/external clients.
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    # Context processors
    @app.context_processor
    def inject_config():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(16)
        return {
            'DAILY_CALORIE_TARGET': app.config['DAILY_CALORIE_TARGET'],
            'DAILY_PROTEIN_TARGET': app.config['DAILY_PROTEIN_TARGET'],
            'DAILY_FAT_TARGET': app.config['DAILY_FAT_TARGET'],
            'DAILY_CARBS_TARGET': app.config['DAILY_CARBS_TARGET'],
            'STRIPE_ENABLED': app.config.get('STRIPE_ENABLED', False),
            'STRIPE_PUBLISHABLE_KEY': app.config.get('STRIPE_PUBLISHABLE_KEY', ''),
            'csrf_token': session['csrf_token'],
        }
    
    return app

if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=bool(app.config.get('DEBUG', False))
    )
