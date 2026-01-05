import monero.address
from monero.seed import Seed
from quart import Blueprint, request, flash, redirect, url_for
from quart_auth import login_required

from lws.helpers import lws
from lws.models import Wallet, get_random_words


bp = Blueprint("wallet", "wallet")


@bp.route("/wallet/add", methods=["GET", "POST"])
@login_required
async def add():
    form = await request.form
    if form:
        label = form.get("label")
        seed = form.get("seed")
        restore_height = form.get("restore_height", None)
        try:
            seed = Seed(seed)
        except ValueError:
            await flash("Invalid mnemonic seed")
            return ""
        lws._init()
        address = str(seed.public_address())
        svk = str(seed.secret_view_key())
        lws.add_wallet(address, svk)
        if restore_height != "-1":
            lws.rescan(address, int(restore_height))
        w = Wallet(
            address=seed.public_address(),
            label=label if label else get_random_words()
        )
        w.save()
    return redirect(url_for("htmx.show_wallets"))


@bp.route("/wallet/<address>/rescan/<height>")
@login_required
async def rescan(address, height):
    lws.rescan(address, int(height))
    return redirect(url_for("htmx.show_wallets"))


@bp.route("/wallet/<address>/modify/<status>")
@login_required
async def modify(address, status):
    lws.modify_wallet(address, status)
    return redirect(url_for("htmx.show_wallets"))


@bp.route("/wallet/<address>/accept")
@login_required
async def accept(address):
    lws.accept_request(address)
    return redirect(url_for("htmx.show_wallets"))


@bp.route("/wallet/<address>/reject")
@login_required
async def reject(address):
    lws.reject_request(address)
    return redirect(url_for("htmx.show_wallets"))


@bp.route("/wallet/<address>/label/<label>")
@login_required
async def label(address, label):
    w = Wallet.select().where(Wallet.address == address).first()
    if w and label:
        w.label = label
        w.save()
    return redirect(url_for("htmx.show_wallets"))
