from flask import Flask, render_template, render_template_string
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Detect if running directly
_IS_MAIN = __name__ == "__main__"

# Handle both direct execution and module import
if _IS_MAIN:
    # When run directly, add parent directory to path and use absolute imports
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from src.extensions import db, login_manager, bcrypt, csrf
else:
    # When imported as module, use relative imports
    from .extensions import db, login_manager, bcrypt, csrf


def create_app(test_config: dict | None = None) -> Flask:
    # Determine the correct paths for templates and static files
    # Flask's root_path is the directory containing the script
    # So when run directly, root_path = src/, and template_folder="views" works
    # When imported, root_path = project root, so we need "src/views"
    if _IS_MAIN:
        # When run directly (python src/app.py), root_path is src/, so use relative paths
        template_dir = "views"
        static_dir = "static"
    else:
        # When imported as module, root_path might be different
        # Use relative paths from the package location
        template_dir = "views"
        static_dir = "static"
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)

    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-key-change-me"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///campus_resource_hub.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=10 * 1024 * 1024,  # 10 MB uploads
        WTF_CSRF_ENABLED=True,
        TEMPLATES_AUTO_RELOAD=True,  # Auto-reload templates in development
        DEBUG=True,  # Enable debug mode to see detailed errors
    )
    if test_config:
        app.config.update(test_config)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Context processor for CSRF token
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        from flask_login import current_user
        unread_count = 0
        if current_user.is_authenticated:
            from src.controllers.messages import get_unread_count
            try:
                unread_count = get_unread_count(current_user.id)
            except Exception:
                pass
        return dict(csrf_token=generate_csrf, unread_message_count=unread_count)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        db.session.rollback()
        return render_template("errors/500.html", error=str(e)), 500

    # Register blueprints - force reload modules when running directly
    if _IS_MAIN:
        import importlib
        import src.controllers.auth
        import src.controllers.resources
        import src.controllers.bookings
        import src.controllers.messages
        import src.controllers.admin
        import src.controllers.ai
        import src.controllers.reviews
        import src.controllers.chatbot
        
        # Reload to ensure we have latest code
        importlib.reload(src.controllers.auth)
        importlib.reload(src.controllers.resources)
        importlib.reload(src.controllers.bookings)
        importlib.reload(src.controllers.messages)
        importlib.reload(src.controllers.admin)
        importlib.reload(src.controllers.ai)
        importlib.reload(src.controllers.reviews)
        importlib.reload(src.controllers.chatbot)
        
        from src.controllers.auth import bp as auth_bp
        from src.controllers.resources import bp as resources_bp
        from src.controllers.bookings import bp as bookings_bp
        from src.controllers.messages import bp as messages_bp
        from src.controllers.admin import bp as admin_bp
        from src.controllers.ai import bp as ai_bp
        from src.controllers.reviews import bp as reviews_bp
        from src.controllers.chatbot import bp as chatbot_bp
    else:
        from .controllers.auth import bp as auth_bp
        from .controllers.resources import bp as resources_bp
        from .controllers.bookings import bp as bookings_bp
        from .controllers.messages import bp as messages_bp
        from .controllers.admin import bp as admin_bp
        from .controllers.ai import bp as ai_bp
        from .controllers.reviews import bp as reviews_bp
        from .controllers.chatbot import bp as chatbot_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp, url_prefix="/ai")
    app.register_blueprint(reviews_bp)
    app.register_blueprint(chatbot_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    # CLI to init DB
    @app.cli.command("db-init")
    def db_init():
        if _IS_MAIN:
            from src.models.models import BaseModel  # ensure models imported
            from src.models.models import User
            from src.extensions import bcrypt
        else:
            from .models.models import BaseModel  # ensure models imported
            from .models.models import User
            from .extensions import bcrypt
        db.create_all()
        # Create a sample admin user if none exists
        if not User.query.filter_by(role="admin").first():
            admin = User(
                email="admin@campus.edu",
                name="Administrator",
                role="admin",
                password_hash=bcrypt.generate_password_hash("admin123").decode()
            )
            db.session.add(admin)
            db.session.commit()
            print("Database initialized. Admin user created: admin@campus.edu / admin123")
        else:
            print("Database initialized.")

    return app


# For `flask run` without FLASK_APP pointing to create_app
app = create_app()

# Allow direct execution
if __name__ == "__main__":
    # Enable template auto-reload in debug mode and disable caching
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable static file caching
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}  # Clear Jinja2 template cache
    
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=True)


