import io
import base64

import qrcode
import monero.seed
from quart import Blueprint, redirect, request, flash, render_template
from quart_auth import login_required

from lws.models import User
from lws.helpers import lws, get_tor_hostname
from lws import config


bp = Blueprint("meta", "meta")


@bp.route("/")
@login_required
async def index():
    admin = User.select().first()
    lws.init(admin.view_key)
    tor_hostname = get_tor_hostname()
    tor_url = f"http://{tor_hostname}:{config.LWS_RPC_PORT}"
    img = qrcode.make(tor_url)
    buffered = io.BytesIO()
    img.save(buffered, format="png")
    img_bytes = buffered.getvalue()
    img_base64_bytes = base64.b64encode(img_bytes)
    img_base64_string = img_base64_bytes.decode("utf-8")

    return await render_template(
        "index.html",
        config=config,
        qrcode=img_base64_string,
        tor_url=tor_url
    )


@bp.route("/utils")
async def utils():
    return await render_template("utils/index.html")


@bp.route("/utils/mnemonic", methods=["GET", "POST"])
async def utils_mnemonic():
    form = await request.form
    if form:
        seed = form.get("seed", "")
        if not seed:
            await flash("must provide mnemonic seed")
            return redirect("/utils/mnemonic")
        try:
            s = monero.seed.Seed(seed)
            return await render_template(
                "utils/mnemonic.html",
                results=s
            )
        except Exception as e:
            print(f"failed to read mnemonic seed: {e}")
            await flash("failed to parse mnemonic seed")
    return await render_template("utils/mnemonic.html")

