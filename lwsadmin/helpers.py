from monero.wallet import Wallet
from monero.daemon import Daemon

from lwsadmin import config

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