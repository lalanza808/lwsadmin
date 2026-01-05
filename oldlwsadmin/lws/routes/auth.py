import monero.address
from quart import Blueprint, redirect, request, flash, render_template
from quart_auth import login_user, AuthUser, current_user, logout_user

from lws.factory import bcrypt
from lws.models import User


bp = Blueprint('auth', 'auth')


@bp.route("/login", methods=["GET", "POST"])
async def login():
    if not User.select().first():
        await flash("must setup first")
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
        address = form.get("address", "")
        view_key = form.get("view_key", "")
        valid_view_key = False
        if not username:
            await flash("must provide a username")
            return redirect("/setup")
        if not password:
            await flash("must provide a password")
            return redirect("/setup")
        if not address:
            await flash("must provide an LWS admin address")
            return redirect("/setup")
        if not view_key:
            await flash("must provide an LWS admin view_key")
            return redirect("/setup")
        try:
            _a = monero.address.Address(address)
            valid_view_key = _a.check_private_view_key(view_key)
        except ValueError:
            await flash("Invalid Monero address")
            return redirect("/setup")
        if not valid_view_key:
            await flash("Invalid view key provided for address")
            return redirect("/setup")
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        admin = User.create(
            username=username,
            password=pw_hash,
            address=address,
            view_key=view_key
        )
        admin.save()
        login_user(AuthUser(admin.id))
        return redirect("/")
    return await render_template("setup.html")
