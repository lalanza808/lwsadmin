import io
import base64

from monero.address import Address as MoneroAddress
from monero.numbers import to_atomic
from flask import Blueprint, render_template, request, flash, redirect

import qrcode
from lwsadmin.helpers import daemon, wallet
from lwsadmin.models import db, Account, Payment
from lwsadmin import config


bp = Blueprint("account", "account")


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = request.form
    if form:
        address = form.get("address", "")
        view_key = form.get("view_key", "")
        valid_view_key = False
        if not address:
            flash("You must provide a primary address")
            return redirect("/register")
        if not view_key:
            flash("You must provide a private view key")
            return redirect("/register")
        try:
            _a = MoneroAddress(address)
            valid_view_key = _a.check_private_view_key(view_key)
        except ValueError:
            flash("Invalid Monero address")
            return redirect("/register")
        if not valid_view_key:
            flash("Invalid view key provided for address")
            return redirect("/register")
        if config.PRICE_PICOS_PER_BLOCK > 0:
            try:
                height = daemon.height()
                new_address = wallet.new_address(label=address)
                account = Account(
                    address=address,
                    view_key=view_key,
                    payment_account_id=0,
                    payment_address_id=new_address[1],
                    payment_address=str(new_address[0]),
                    start_height=height
                )
                db.session.add(account)
                db.session.commit()
                return redirect(f"/account/{address}/{view_key}")
            except Exception as e:
                flash("There was an error with your request:", str(e))
                return redirect("/register")
        return redirect(f"/account/{address}/{view_key}")
    return render_template(
        "pages/register.html"
    )

@bp.route("/account/<address>/<view_key>", methods=["GET", "POST"])
def account(address, view_key):
    account = Account.query.filter(Account.address == address).first()
    img = qrcode.make(f"monero:{account.payment_address}?tx_description='Funding blocks for LWS service'")
    buffered = io.BytesIO()
    img.save(buffered, format="png")
    img_bytes = buffered.getvalue()
    img_base64_bytes = base64.b64encode(img_bytes)
    img_base64_string = img_base64_bytes.decode("utf-8")
    txes = wallet.incoming(local_address=account.payment_address, unconfirmed=True)
    pending_txes = []
    completed_txes = []
    
    for tx in txes:
        raw_params = {"txid": tx.transaction.hash, "account_index": account.payment_account_id}
        raw_tx = wallet._backend.raw_request("get_transfer_by_txid", raw_params)["transfer"]
        if raw_tx["unlock_time"] > 0:
            print(f"{tx.transaction.hash} unlock time greater than 0, ignoring")
            continue
        if raw_tx["locked"]:
            pending_txes.append(raw_tx)
        else:
            completed_txes.append(raw_tx)
            tx_exists = Payment.query.filter(Payment.tx_hash == tx.transaction.hash).first()
            if not tx_exists:
                print(f"tx {tx.transaction.hash} does not exist in the db yet.")
                tx_confs = wallet.confirmations(tx)
                print(tx_confs)
                payment = Payment(
                    tx_hash=tx.transaction.hash,
                    account_id=account.id,
                    amount=raw_tx["amount"],
                    price_per_block=config.PRICE_PICOS_PER_BLOCK,
                    confirmed=True,
                    dropped=False
                )
                db.session.add(payment)
                db.session.commit()
    
    payments = Payment.query.filter(Payment.account_id == account.id)
    for p in payments:
        print(f"price per block: {p.price_per_block}. amount sent: {p.amount}")
        print(p.amount / p.price_per_block)
    
    return render_template(
        "pages/account.html",
        address=account.payment_address,
        view_key=account.view_key,
        qrcode=img_base64_string,
        txes=txes,
        account=account,
        pending_txes=pending_txes,
        completed_txes=completed_txes,
        payments=payments
    )

