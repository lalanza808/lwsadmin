from quart import Blueprint, render_template, request
from monero.seed import Seed
from quart_auth import login_required

from lws.models import Wallet
from lws.helpers import LWS

bp = Blueprint('htmx', 'htmx', url_prefix="/htmx")


@bp.route("/create_wallet")
@login_required
async def create_wallet():
    """Creating a new wallet with newly generated seeds"""
    seed = Seed()
    return await render_template(
        "htmx/create_wallet.html",
        seed=seed.phrase,
        address=seed.public_address(),
        psk=seed.public_spend_key(),
        pvk=seed.public_view_key(),
        ssk=seed.secret_spend_key(),
        svk=seed.secret_view_key()
    )


@bp.route("/import_wallet")
@login_required
async def import_wallet():
    """Importing an existing wallet"""
    return await render_template("htmx/import_wallet.html")


@bp.route("/label_wallet")
@login_required
async def label_wallet():
    """Changing the label on a stored wallet"""
    address = request.args.get("address")
    label = request.args.get("label")
    return await render_template(
        "htmx/label_wallet.html", 
        address=address, 
        label=label
    )


@bp.route("/set_height")
@login_required
async def set_height():
    """Setting a new height to scan from"""
    address = request.args.get("address")
    height = request.args.get("height")
    return await render_template(
        "htmx/set_height.html",
        address=address,
        height=height
    )


@bp.route("/show_wallets")
@login_required
async def show_wallets():
    """Showing all wallets in the database in a table"""
    lws = LWS()
    accounts = lws.list_accounts()
    if "hidden" in accounts:
        del accounts["hidden"]
    # save wallets if they don't exist in the db
    for status in accounts:
        for account in accounts[status]:
            w = Wallet.select().where(Wallet.address == account["address"]).first()
            if not w:
                w = Wallet(
                    address=account["address"]
                )
                w.save()
    requests = lws.list_requests()
    print(requests)
    if "import" in requests:
        del requests["import"]
    return await render_template(
        "htmx/show_wallets.html",
        accounts=accounts,
        requests=requests
    )
