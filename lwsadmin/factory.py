from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from lwsadmin import config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_PROTECTION"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    login_manager.login_view = "auth.login"
    
    with app.app_context():
        from lwsadmin.models import User
        from lwsadmin.routes import home, auth, account, api
        from lwsadmin import filters

        @login_manager.user_loader
        def load_user(user_id: str):
            return User.query.filter(User.id == user_id).first()

        # from lwsadmin import filters, cli
        app.register_blueprint(home.bp)
        app.register_blueprint(api.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(account.bp)
        app.register_blueprint(filters.bp)
        return app