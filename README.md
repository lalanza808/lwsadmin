# lwsadmin

Monero lightwallet project. Packages the following services in one package:

* `monero-lws` by [vtnerd](https://github.com/vtnerd/monero-lws) - scans your wallet's view keys in the background
* `lwsadmin` by lza_menace - backend CRUD app for managing the LWS backend
* `monerod` by [The Monero Project](https://github.com/monero-project/monero) - node for syncing Monero blockchain transactions

## Running

The default compose stack pulls in images which were pre-built for ease of use.

Clone the repo and run: `docker-compose up -d`

- `lwsadmin` will be available at http://127.0.0.1:5000
- `monero-lws` will be available at http://127.0.0.1:8080 (rpc) and http://127.0.0.1:8081 (admin)
- `monerod` will be available at :18080 (p2p), :18081 (unrestricted rpc), :18082 (zmq), and :18089 (restricted rpc)

Before finishing you need to setup `lwsadmin` with credentials to manage `monero-lws`. Run the following to generate a new admin user in LWS:

```bash
docker exec -ti monero-lws monero-lws-admin create_admin
```

Proceed to setup your user at http://127.0.0.1:5000/setup - use the LWS admin address and key from the previous command.

Start adding wallets.

### Links

* https://github.com/moneroexamples/openmonero
* http://github.com/vtnerd/monero-lws/blob/master/docs/administration.md
* https://github.com/monero-project/meta/blob/master/api/lightwallet_rest.md
* https://github.com/CryptoGrampy/monero-lws-admin
* https://www.npmjs.com/package/@mymonero/mymonero-wallet-manager/v/3.0.0
* https://github.com/mymonero/mymonero-utils/tree/master/packages/mymonero-lws-client
* https://github.com/mymonero/mymonero-utils/tree/master/packages/mymonero-monero-client
* https://github.com/mymonero/mymonero-utils/tree/master/packages/mymonero-wallet-manager

### Notes

```
accept_requests: {"type": "import"|"create", "addresses":[...]}
add_account: {"address": ..., "key": ...}
list_accounts: {}
list_requests: {}
modify_account_status: {"status": "active"|"hidden"|"inactive", "addresses":[...]}
reject_requests: {"type": "import"|"create", "addresses":[...]}
rescan: {"height":..., "addresses":[...]}
webhook_add: {"type":"tx-confirmation", "address":"...", "url":"...", ...} with optional fields:
    token: A string to be returned when the webhook is triggered
    payment_id: 16 hex characters representing a unique identifier for a transaction
webhook_delete
```