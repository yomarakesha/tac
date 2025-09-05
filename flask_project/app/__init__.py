from flask import Flask
from .models import db, AdminUser
from .admin import create_admin  # убрали login_manager
from .routes.auth import auth_bp
from flask_babel import Babel
from .routes.api import api_bp
from flask_login import LoginManager
from flask_migrate import Migrate

babel = Babel()
login_manager = LoginManager()  # теперь здесь
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # user_loader для Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    create_admin(app)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()
    
    babel.init_app(app)
    app.register_blueprint(api_bp, url_prefix="/api")
    return app
