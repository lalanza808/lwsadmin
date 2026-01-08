from flask import Blueprint

from lwsadmin.library.lws import LWS
from lwsadmin.helpers import daemon
from lwsadmin.models import db, Account, Payment, User

bp = Blueprint('cli', 'cli')


@bp.cli.command("debug")
def debug():
    user = User.query.filter().first()
    lws = LWS(user.view_key)
    print("accounts")
    accounts = lws.list_accounts()
    if 'hidden' in accounts:
        del accounts["hidden"]
    print(accounts)
    requests = lws.list_requests()
    print(requests)
    print()
    accounts = Account.query.filter()
    for account in accounts:
        payments = Payment.query.filter(Payment.account_id == account.id)
        payments_json = [p.as_json() for p in payments]
        height = daemon.height()
        total_sent = sum([p["amount"] for p in payments_json])
        total_blocks_to_scan = sum([p.get_blocks_to_scan() for p in payments])
        max_height = account.start_height + total_blocks_to_scan
        remaining_blocks = account.start_height + total_blocks_to_scan - height
        # only look at accounts that have sent funds
        if total_sent:
            if max_height > height:
                # lws.rescan(account.address, account.start_height)
                if not account.active:
                    lws.accept_request(account.address)
                    account.active = True
                    db.session.commit()
                    print(f"account for address {account.address[-6:]} has {remaining_blocks} more blocks, marked as active")
            else:
                if account.active:
                    lws.modify_wallet(account.address, 'inactive')
                    account.active = False
                    db.session.commit()
                    print(f"account for address {account.address[-6:]} should not be marked as active")

        # get_address_info
        # get_wallet
        # exists
        # list_accounts
        # list_requests
        # get_address_txs
        
        # address_info = lws.get_address_info(account.address, account.view_key)
        # print(address_info)
        