from quart import Blueprint, redirect, request, flash, render_template
from quart_auth import login_user, AuthUser, current_user, logout_user

from lws.factory import bcrypt
from lws.models import User


bp = Blueprint('auth', 'auth')


@bp.route("/login", methods=["GET", "POST"])
async def login():
    if not User.select().first():
        await flash("must setup your user first")
        return redirect("/setup")
    form = await request.form
    if form:
        username = form.get("username", "")
        password = form.get("password", "")
        if not username:
            await flash("must provide a username")
            return redirect("/login")
        if not password:
            await flash("must provide a password")
            return redirect("/login")
        user = User.select().where(User.username == username).first()
        if not user:
            await flash("this user does not exist")
            return redirect("/login")
        pw_matches = bcrypt.check_password_hash(user.password, password)
        if not pw_matches:
            await flash("invalid password")
            return redirect("/login")
        login_user(AuthUser(user.id))
        nxt = request.args.get("next")
        if nxt:
            return redirect(nxt)
        return redirect("/")
    return await render_template("login.html")


@bp.route("/logout")
async def logout():
    if await current_user.is_authenticated:
        logout_user()
    return redirect("/")


@bp.route("/setup", methods=["GET", "POST"])
async def setup():
    if User.select().first():
        await flash("Setup already completed")
        return redirect("/")
    form = await request.form
    if form:
        username = form.get("username", "")
        password = form.get("password", "")
        if not username:
            await flash("must provide a username")
            return redirect("/setup")
        if not password:
            await flash("must provide a password")
            return redirect("/setup")
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        admin = User.create(
            username=username,
            password=pw_hash
        )
        admin.save()
        login_user(AuthUser(admin.id))
        return redirect("/")
    return await render_template("setup.html")
