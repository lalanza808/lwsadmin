import re

from quart import Blueprint, redirect, request, flash, render_template
from quart_auth import login_user, AuthUser, current_user, logout_user

from lws import config
from lws.helpers import LWS
from lws.models import Wallet


bp = Blueprint('auth', 'auth')


@bp.route("/login", methods=["GET", "POST"])
async def login():
    if await current_user.is_authenticated:
        return redirect("/admin")
    form = await request.form
    if form:
        password = form.get("password", "")
        if not password:
            await flash("must provide a password")
            return redirect("/login")
        if not config.ADMIN_PASSWORD:
            await flash("admin password not configured on this server")
            return redirect("/login")
        if password != config.ADMIN_PASSWORD:
            await flash("invalid password")
            return redirect("/login")
        login_user(AuthUser("admin"))
        nxt = request.args.get("next")
        if nxt:
            return redirect(nxt)
        return redirect("/admin")
    return await render_template("login.html")


@bp.route("/logout")
async def logout():
    if await current_user.is_authenticated:
        logout_user()
    return redirect("/")


@bp.route("/register", methods=["GET", "POST"])
async def register():
    form = await request.form
    if form:
        email_address = form.get("email_address", "").strip()
        public_address = form.get("public_address", "").strip()
        secret_view_key = form.get("secret_view_key", "").strip()
        label = form.get("label", "").strip()

        # Validate all required fields
        if not email_address:
            await flash("email address is required")
            return redirect("/register")
        if not public_address:
            await flash("public address is required")
            return redirect("/register")
        if not secret_view_key:
            await flash("secret view key is required")
            return redirect("/register")
        if not label:
            await flash("label is required")
            return redirect("/register")

        # Length checks
        if len(email_address) > 150:
            await flash("email too long")
            return redirect("/register")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email_address):
            await flash("invalid email address format")
            return redirect("/register")
        if len(public_address) > 200:
            await flash("public address too long")
            return redirect("/register")
        if len(secret_view_key) > 200:
            await flash("secret view key too long")
            return redirect("/register")
        if len(label) > 80:
            await flash("label too long")
            return redirect("/register")

        # Validate Monero address format (95 chars, starts with 4)
        if len(public_address) != 95 or not public_address.startswith("4"):
            await flash("invalid Monero public address")
            return redirect("/register")

        # Validate view key is 64 hex chars
        if len(secret_view_key) != 64:
            await flash("secret view key must be 64 hex characters")
            return redirect("/register")
        try:
            int(secret_view_key, 16)
        except ValueError:
            await flash("secret view key must be valid hexadecimal")
            return redirect("/register")

        # Check if already registered locally
        existing = Wallet.select().where(
            Wallet.public_address == public_address
        ).first()
        if existing:
            await flash("this address is already registered")
            return redirect("/register")

        # Ensure wallet is active in LWS.
        # This handles three cases:
        #   1. User connected via Skylight first -> pending create request -> accept it
        #   2. Wallet exists but inactive/hidden -> modify to active
        #   3. Brand new wallet -> add_account (starts scanning from current height)
        lws = LWS()
        try:
            success, msg = lws.ensure_active(public_address, secret_view_key)
            if not success:
                await flash(f"failed to activate wallet in LWS: {msg}")
                return redirect("/register")
        except Exception as e:
            await flash(f"failed to register wallet with LWS: {e}")
            return redirect("/register")

        # Save to local database
        w = Wallet(
            email_address=email_address,
            public_address=public_address,
            secret_view_key=secret_view_key,
            label=label
        )
        w.save()

        await flash(
            "wallet registered successfully! "
            "it will begin scanning from the current block height."
        )
        return redirect("/")

    return await render_template("register.html")
