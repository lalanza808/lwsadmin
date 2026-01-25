from monero.wallet import Wallet
from monero.daemon import Daemon
from monero.address import Address

from lwsadmin import config
from lwsadmin.models import Account

daemon = Daemon(
    port=config.MONEROD_PORT,
    protocol=config.MONEROD_PROTO,
    host=config.MONEROD_HOST
)

wallet = Wallet(
    port=config.WALLET_RPC_PORT, 
    user=config.WALLET_RPC_USERNAME, 
    password=config.WALLET_RPC_PASSWORD
)

def generate_address() -> None|Address:
    available = False
    attempts = 0
    max_attempts = 20
    while not available:
        if attempts >= max_attempts:
            print("max attempts at generating new address. an admin must intervene")
            break
        new_address = wallet.new_address()
        addr = str(new_address[0])
        address_used = Account.query.filter(Account.payment_address == addr)
        if address_used.first():
            print(f"{addr} already used, trying again")
            attempts += 1
        else:
            return new_address

