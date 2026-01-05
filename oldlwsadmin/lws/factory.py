from quart import Quart, redirect, request
from quart_auth import (
    AuthManager, Unauthorized
)
from quart_bcrypt import Bcrypt

from lws import config


def create_app():
    app = Quart(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["DEBUG"] = config.DEBUG
    app.config["TEMPLATES_AUTO_RELOAD"] = config.TEMPLATES_AUTO_RELOAD
    app.config["QUART_ENV"] = config.QUART_ENV
    app.config["QUART_AUTH_DURATION"] = config.QUART_AUTH_DURATION
    app.config["SERVER_NAME"] = config.SERVER_NAME
    AuthManager(app)
    bcrypt = Bcrypt(app)
    
    @app.before_serving
    async def startup():
        from lws.routes import auth, wallet, meta, htmx
        from lws import filters
        app.register_blueprint(filters.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(meta.bp)
        app.register_blueprint(wallet.bp)
        app.register_blueprint(htmx.bp)

    @app.errorhandler(Unauthorized)
    async def redirect_to_login(*_):
        if request.path == "/":
            return redirect(f"/login?next={request.path}")
        else:
            return f"<p>you need to authenticate first</p><a href=\"/login\">login</a>"
    
    return app
    
bcrypt = Bcrypt(create_app())