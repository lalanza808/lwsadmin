import requests

from lwsadmin.models import User
from lwsadmin import config


# accept_requests: {"type": "import"|"create", "addresses":[...]}
# add_account: {"address": ..., "key": ...}
# list_accounts: {}
# list_requests: {}
# modify_account_status: {"status": "active"|"hidden"|"inactive", "addresses":[...]}
# reject_requests: {"type": "import"|"create", "addresses":[...]}
# rescan: {"height":..., "addresses":[...]}
# webhook_add: {"type":"tx-confirmation", "address":"...", "url":"...", ...} with optional fields:
#     token: A string to be returned when the webhook is triggered
#     payment_id: 16 hex characters representing a unique identifier for a transaction
# webhook_delete: {"addresses":[...]}
# webhook_delete_uuid: {"event_ids": [...]}
# webhook_list: {}

class LWS:
    def __init__(self, admin_key):
        self.admin_key = admin_key
        pass
    
    def get_address_info(self, address, view_key):
        endpoint = f"{config.LWS_URL}/get_address_info"
        data = {
            "address": address,
            "view_key": view_key
        }
        r = requests.post(endpoint, json=data, timeout=5)
        r.raise_for_status()
        return r.json()
    
    def get_wallet(self, address: str) -> dict:
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
    
    def exists(self, address: str) -> bool:
        try:
            res = self.get_wallet(address)
            return False if res == {} else True
        except Exception as e:
            print(f"Failed to check wallet active: {e}")
            return False
    
    def list_accounts(self) -> dict:
        endpoint = f"{config.LWS_ADMIN_URL}/list_accounts"
        data = {"auth": self.admin_key}
        try:
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
        data = {"auth": self.admin_key}
        try:
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
        data = {
            "auth": self.admin_key, 
            "params": {
                "address": address, 
                "key": view_key
            }
        }
        try:
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
        data = {
            "auth": self.admin_key, 
            "params": {
                "addresses": [address], 
                "status": status
            }
        }
        try:
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
        data = {
            "auth": self.admin_key, 
            "params": {
                "addresses": [address], 
                "type": req_type
            }
        }
        try:
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
        data = {
            "auth": self.admin_key, 
            "params": {
                "addresses": [address], 
                "type": req_type
            }
        }
        try:
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
        data = {
            "auth": self.admin_key, 
            "params": {
                "addresses": [address], 
                "height": height
            }
        }
        try:
            req = requests.post(endpoint, json=data, timeout=5)
            req.raise_for_status()
            if req.ok:
                return req.json()
            return {}
        except Exception as e:
            print(f"Failed to rescan wallet {address}: {e}")
            return {}

