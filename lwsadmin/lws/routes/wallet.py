from quart import Blueprint, redirect, url_for
from quart_auth import login_required

from lws.helpers import LWS
from lws.models import Wallet


bp = Blueprint("wallet", "wallet")


@bp.route("/wallet/<address>/rescan/<height>")
@login_required
async def rescan(address, height):
    lws = LWS()
    lws.rescan(address, int(height))
    return redirect(url_for("htmx.show_wallets"))


@bp.route("/wallet/<address>/modify/<status>")
@login_required
async def modify(address, status):
    lws = LWS()
    lws.modify_wallet(address, status)
    return redirect(url_for("htmx.show_wallets"))


@bp.route("/wallet/<address>/accept")
@login_required
async def accept(address):
    lws = LWS()
    lws.accept_request(address)
    return redirect(url_for("htmx.show_wallets"))


@bp.route("/wallet/<address>/reject")
@login_required
async def reject(address):
    lws = LWS()
    lws.reject_request(address)
    return redirect(url_for("htmx.show_wallets"))


@bp.route("/wallet/<address>/label/<label>")
@login_required
async def label(address, label):
    w = Wallet.select().where(Wallet.public_address == address).first()
    if w and label:
        w.label = label
        w.save()
    return redirect(url_for("htmx.show_wallets"))
