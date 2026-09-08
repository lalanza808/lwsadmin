import io
import base64

import qrcode
from quart import Blueprint, render_template
from quart_auth import login_required

from lws.helpers import get_tor_hostname, LWS
from lws import config


def make_qr_base64(data: str) -> str:
    """Generate a base64-encoded PNG QR code for the given string."""
    img = qrcode.make(data)
    buffered = io.BytesIO()
    img.save(buffered, format="png")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


bp = Blueprint("meta", "meta")


@bp.route("/")
async def index():
    """Public landing page with connection info and link to register."""
    tor_hostname = get_tor_hostname()
    tor_url = ""
    tor_qr = ""
    if tor_hostname:
        tor_url = f"http://{tor_hostname}:{config.LWS_RPC_PORT}"
        tor_qr = make_qr_base64(tor_url)
    clearnet_qr = make_qr_base64(config.LWS_EXTERNAL_URL)
    return await render_template(
        "index.html",
        config=config,
        tor_qr=tor_qr,
        clearnet_qr=clearnet_qr,
        tor_url=tor_url,
    )


@bp.route("/about")
async def about():
    """Public about page describing the service and its operator."""
    return await render_template("about.html")


@bp.route("/admin")
@login_required
async def admin():
    """Admin dashboard for managing wallets. Requires login."""
    tor_hostname = get_tor_hostname()
    tor_url = ""
    if tor_hostname:
        tor_url = f"http://{tor_hostname}:{config.LWS_RPC_PORT}"
    lws = LWS()
    current_height = lws.get_current_height()
    return await render_template(
        "admin.html",
        config=config,
        tor_url=tor_url,
        current_height=current_height
    )
