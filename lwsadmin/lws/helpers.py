import json
from pathlib import Path

import requests

from lws import config

def get_tor_hostname():
    hostname_path = Path(config.TOR_HOSTNAME_PATH)
    if not hostname_path.exists():
        return ""
    with open(hostname_path, "r") as f:
        return f.read().strip()

def get_lws_keys():
    try:
        with open(config.LWS_KEY_PATH, "r") as f:
            data = json.loads(f.read())
            return data
    except Exception:
        return None

# accept_requests: {"type": "import"|"create", "addresses":[...]}
# add_account: {"address": ..., "key": ...}
# list_accounts: {}
# list_requests: {}
# modify_account_status: {"status": "active"|"hidden"|"inactive", "addresses":[...]}
# reject_requests: {"type": "import"|"create", "addresses":[...]}
# rescan: {"height":..., "addresses":[...]}
# webhook_add: {"type":"tx-confirmation", "address":"...", "url":"..."}
#   with optional fields:
#     token: A string to be returned when the webhook is triggered
#     payment_id: 16 hex characters representing a unique identifier for a transaction
# webhook_delete: {"addresses":[...]}
# webhook_delete_uuid: {"event_ids": [...]}
# webhook_list: {}

class LWS:
    def __init__(self):
        self.data = get_lws_keys()
        if self.data is None:
            print("[WARNING] LWS admin credentials not found or unreadable at "
                  f"{config.LWS_KEY_PATH} - admin API calls will fail")
            self.data = {"key": ""}

    def get_address_info(self, address, view_key):
        endpoint = f"{config.LWS_URL}/get_address_info"
        data = {
            "address": address,
            "view_key": view_key
        }
        r = requests.post(endpoint, json=data, timeout=5)
        r.raise_for_status()
        return r.json()

    def get_current_height(self) -> int:
        """Get the current blockchain height from LWS.

        Uses the admin account's own address to query get_address_info,
        which returns blockchain_height. Falls back to list_accounts
        to find the highest scan_height among active accounts.
        Returns 0 if unable to determine height.
        """
        try:
            accounts = self.list_accounts()
            if "active" in accounts and accounts["active"]:
                # The scan_height from list_accounts gives us a reasonable
                # approximation; for the actual blockchain_height we'd need
                # the view key. Use the highest scan_height as a floor.
                max_height = max(
                    a.get("scan_height", 0)
                    for a in accounts["active"]
                )
                return max_height
            return 0
        except Exception as e:
            print(f"Failed to get current height: {e}")
            return 0

    def get_wallet(self, address: str) -> dict:
        """Look up a wallet across all account statuses.
        Returns the account dict with a 'status' field, or {} if not found.
        """
        try:
            res = self.list_accounts()
            for _status in res:
                for _wallet in res[_status]:
                    if _wallet["address"] == address:
                        _wallet["status"] = _status
                        return _wallet
            return {}
        except Exception as e:
            print(f"Failed to check wallet active: {e}")
            return {}

    def get_request(self, address: str) -> dict:
        """Look up a wallet in pending requests (create/import).
        Returns {"type": "create"|"import", "address": ..., ...} or {} if not found.
        """
        try:
            res = self.list_requests()
            for req_type in res:
                for req in res[req_type]:
                    if req["address"] == address:
                        req["type"] = req_type
                        return req
            return {}
        except Exception as e:
            print(f"Failed to check wallet request: {e}")
            return {}

    def exists(self, address: str) -> bool:
        try:
            res = self.get_wallet(address)
            return False if res == {} else True
        except Exception as e:
            print(f"Failed to check wallet active: {e}")
            return False

    def ensure_active(self, address: str, view_key: str) -> tuple[bool, str]:
        """Ensure a wallet is actively scanning in LWS.

        Handles three cases:
        1. Address has a pending create request -> accept it
        2. Address exists in accounts but is inactive -> modify to active
        3. Address doesn't exist at all -> add_account

        Returns (success: bool, message: str).
        """
        # Case 1: Check pending requests first
        pending = self.get_request(address)
        if pending:
            req_type = pending.get("type", "create")
            self.accept_request(address, req_type)
            return (True, "accepted pending request")

        # Case 2: Check existing accounts (inactive, hidden, or already active)
        wallet = self.get_wallet(address)
        if wallet:
            status = wallet.get("status", "")
            if status == "active":
                return (True, "wallet is already active")
            # inactive or hidden -> set to active
            self.modify_wallet(address, "active")
            return (True, f"activated wallet (was {status})")

        # Case 3: Brand new wallet, not in LWS at all
        self.add_wallet(address, view_key)
        return (True, "added new wallet")

    def list_accounts(self) -> dict:
        endpoint = f"{config.LWS_ADMIN_URL}/list_accounts"
        try:
            data = {"auth": self.data["key"]}
            req = requests.post(endpoint, json=data, timeout=5)
            req.raise_for_status()
            if req.ok:
                return req.json()
            return {}
        except Exception as e:
            print(f"Failed to list accounts: {e}")
            return {}

    def list_requests(self) -> dict:
        endpoint = f"{config.LWS_ADMIN_URL}/list_requests"
        try:
            data = {"auth": self.data["key"]}
            req = requests.post(endpoint, json=data, timeout=5)
            req.raise_for_status()
            if req.ok:
                return req.json()
            return {}
        except Exception as e:
            print(f"Failed to list accounts: {e}")
            return {}

    def get_address_txs(self, address: str, view_key: str) -> dict:
        endpoint = f"{config.LWS_URL}/get_address_txs"
        data = {
            "address": address,
            "view_key": view_key
        }
        try:
            req = requests.post(endpoint, json=data, timeout=5)
            req.raise_for_status()
            if req.ok:
                return req.json()
            return {}
        except Exception as e:
            print(f"Failed to get wallet info {address}: {e}")
            return {}

    def add_wallet(self, address: str, view_key: str) -> dict:
        endpoint = f"{config.LWS_ADMIN_URL}/add_account"
        try:
            data = {
                "auth": self.data["key"],
                "params": {
                    "address": address,
                    "key": view_key
                }
            }
            req = requests.post(endpoint, json=data, timeout=5)
            req.raise_for_status()
            if req.ok:
                return req.json()
            return {}
        except Exception as e:
            print(f"Failed to add wallet {address}: {e}")
            return {}

    def modify_wallet(self, address: str, status: str) -> dict:
        endpoint = f"{config.LWS_ADMIN_URL}/modify_account_status"
        try:
            data = {
                "auth": self.data["key"],
                "params": {
                    "addresses": [address],
                    "status": status
                }
            }
            req = requests.post(endpoint, json=data, timeout=5)
            req.raise_for_status()
            if req.ok:
                return req.json()
            return {}
        except Exception as e:
            print(f"Failed to modify wallet {address}: {e}")
            return {}

    def accept_request(self, address: str, req_type: str="create") -> dict:
        endpoint = f"{config.LWS_ADMIN_URL}/accept_requests"
        try:
            data = {
                "auth": self.data["key"],
                "params": {
                    "addresses": [address],
                    "type": req_type
                }
            }
            req = requests.post(endpoint, json=data, timeout=5)
            req.raise_for_status()
            if req.ok:
                return req.json()
            return {}
        except Exception as e:
            print(f"Failed to accept request wallet {address}: {e}")
            return {}

    def reject_request(self, address: str, req_type: str="create") -> dict:
        endpoint = f"{config.LWS_ADMIN_URL}/reject_requests"
        try:
            data = {
                "auth": self.data["key"],
                "params": {
                    "addresses": [address],
                    "type": req_type
                }
            }
            req = requests.post(endpoint, json=data, timeout=5)
            req.raise_for_status()
            if req.ok:
                return req.json()
            return {}
        except Exception as e:
            print(f"Failed to reject request wallet {address}: {e}")
            return {}

    def rescan(self, address: str, height: int) -> dict:
        endpoint = f"{config.LWS_ADMIN_URL}/rescan"
        try:
            data = {
                "auth": self.data["key"],
                "params": {
                    "addresses": [address],
                    "height": height
                }
            }
            req = requests.post(endpoint, json=data, timeout=5)
            req.raise_for_status()
            if req.ok:
                return req.json()
            return {}
        except Exception as e:
            print(f"Failed to rescan wallet {address}: {e}")
            return {}

    def validate(
        self,
        spend_public_hex: str,
        view_public_hex: str,
        view_key_hex: str,
    ) -> dict:
        """Validate spend_public, view_public, and view_key hex values.
        Returns {"address": "..."} on success or {"error": {...}} on failure.
        """
        endpoint = f"{config.LWS_ADMIN_URL}/validate"
        try:
            data = {
                "auth": self.data["key"],
                "params": {
                    "spend_public_hex": spend_public_hex,
                    "view_public_hex": view_public_hex,
                    "view_key_hex": view_key_hex
                }
            }
            req = requests.post(endpoint, json=data, timeout=5)
            req.raise_for_status()
            if req.ok:
                return req.json()
            return {}
        except Exception as e:
            print(f"Failed to validate keys: {e}")
            return {}


lws = LWS()
