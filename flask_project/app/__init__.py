from flask import Flask
from .models import db, AdminUser
from .admin import create_admin, login_manager
from .routes.auth import auth_bp
from flask_babel import Babel

babel = Babel()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
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
    return app
