from flask import Blueprint

from lwsadmin.helpers import daemon, wallet
from lwsadmin.models import db, Account, Payment

from lwsadmin import config


bp = Blueprint("api", "api", url_prefix="/api")


@bp.route("/blockchain/stats")
def stats():
    return {
        "height": daemon.height()
    }

@bp.route("/account/<address>/<view_key>")
def account(address, view_key):
    account = Account.query.filter(Account.address == address, Account.view_key == view_key).first()
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
    payments_json = [p.as_json() for p in payments]
    height = daemon.height()
    total_sent = sum([p["amount"] for p in payments_json])
    total_blocks_to_scan = sum([p.get_blocks_to_scan() for p in payments])
    max_height = account.start_height + total_blocks_to_scan
    remaining_blocks = account.start_height + total_blocks_to_scan - height

    return {
        "current_height": height,
        "start_height": account.start_height,
        "total_xmr_sent": total_sent,
        "total_blocks_to_scan": total_blocks_to_scan,
        "max_height": max_height,
        "remaining_blocks": max(remaining_blocks, 0),
        "payments": payments_json,
        "transactions": {
            "pending": pending_txes,
            "completed": completed_txes
        }
    }

# the current height is {height}
# this account started at height {account.start_height}
# {height - account.start_height} blocks have been mined since this account came online
# {total_sent} atomic xmr has been sent and is thus entitled to scan for {total_blocks_to_scan} total blocks
# the last block available for scanning will be {account.start_height + total_blocks_to_scan}
# the scanning will continue for {account.start_height + total_blocks_to_scan - height} more blocks