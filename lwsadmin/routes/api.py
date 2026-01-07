from flask import Blueprint

from lwsadmin.helpers import daemon
from lwsadmin.models import Account, Payment


bp = Blueprint("api", "api", url_prefix="/api")


@bp.route("/blockchain/stats")
def stats():
    return {
        "height": daemon.height()
    }

@bp.route("/account/<address>/<view_key>")
def account(address, view_key):
    account = Account.query.filter(Account.address == address, Account.view_key == view_key).first()
    payments = Payment.query.filter(Payment.account_id == account.id)
    height = daemon.height()
    total_sent = sum([p.amount for p in payments])
    total_blocks_to_scan = sum([p.get_blocks_to_scan() for p in payments])
    max_height = account.start_height + total_blocks_to_scan
    remaining_blocks = account.start_height + total_blocks_to_scan - height
    return {
        "current_height": height,
        "start_height": account.start_height,
        "total_xmr_sent": total_sent,
        "total_blocks_to_scan": total_blocks_to_scan,
        "max_height": max_height,
        "remaining_blocks": remaining_blocks
    }

# the current height is {height}
# this account started at height {account.start_height}
# {height - account.start_height} blocks have been mined since this account came online
# {total_sent} atomic xmr has been sent and is thus entitled to scan for {total_blocks_to_scan} total blocks
# the last block available for scanning will be {account.start_height + total_blocks_to_scan}
# the scanning will continue for {account.start_height + total_blocks_to_scan - height} more blocks