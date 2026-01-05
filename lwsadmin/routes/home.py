from flask import Blueprint, render_template, redirect, flash
from flask_login import current_user, login_required

from lwsadmin.library.lws import LWS
from lwsadmin.models import User
# from lwsadmin.helpers import generate_qr
from lwsadmin import config


bp = Blueprint("home", "home")


@bp.route("/")
@login_required
def home():
    print(current_user.username)
    user = User.query.filter()
    lws = LWS(user.first().view_key)
    accounts = lws.list_accounts()
    if 'hidden' in accounts:
        del accounts["hidden"]
    # for status in accounts:
    #     for account in accounts[status]:
    #         w = Wallet.select().where(Wallet.address == account["address"]).first()
    #         if not w:
    #             w = Wallet(
    #                 address=account["address"]
    #             )
    #             w.save()
    requests = lws.list_requests()
    print(requests)
    return render_template(
        "pages/home.html",
        accounts=accounts,
        requests=requests
    )
