import monero.address
from flask import Blueprint, redirect, request, flash, render_template, flash
from flask_login import login_user, current_user, logout_user

from lwsadmin.factory import bcrypt
from lwsadmin.models import db, User


bp = Blueprint("auth", "auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if not User.query.filter().first():
        flash("You must setup your administrator before continuing")
        return redirect("/setup")
    form = request.form
    if form:
        username = form.get("username", "")
        password = form.get("password", "")
        if not username:
            flash("You must provide a username")
            return redirect("/login")
        if not password:
            flash("You must provide a password")
            return redirect("/login")
        user = User.query.filter().where(User.username == username).first()
        if not user:
            flash("This user does not exist")
            return redirect("/login")
        pw_matches = bcrypt.check_password_hash(user.password, password)
        if not pw_matches:
            flash("Invalid password provided")
            return redirect("/login")
        login_user(user)
        print("logged in user")
        nxt = request.args.get("next")
        if nxt:
            return redirect(nxt)
        return redirect("/")
    return render_template("pages/login.html")

@bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect("/")

@bp.route("/setup", methods=["GET", "POST"])
def setup():
    if User.query.filter().first():
        flash("Setup already completed")
        return redirect("/")
    form = request.form
    if form:
        username = form.get("username", "")
        password = form.get("password", "")
        address = form.get("address", "")
        view_key = form.get("view_key", "")
        valid_view_key = False
        if not username:
            flash("You must provide a username")
            return redirect("/setup")
        if not password:
            flash("You must provide a password")
            return redirect("/setup")
        if not address:
            flash("You must provide an LWS admin address")
            return redirect("/setup")
        if not view_key:
            flash("You must provide an LWS admin view_key")
            return redirect("/setup")
        try:
            _a = monero.address.Address(address)
            valid_view_key = _a.check_private_view_key(view_key)
        except ValueError:
            flash("Invalid Monero address")
            return redirect("/setup")
        if not valid_view_key:
            flash("Invalid view key provided for address")
            return redirect("/setup")
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        admin = User(
            username=username,
            password=pw_hash,
            address=address,
            view_key=view_key
        )
        db.session.add(admin)
        db.session.commit()
        login_user(admin)
        return redirect("/")
    return render_template("pages/setup.html")
