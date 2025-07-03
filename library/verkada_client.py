# verkada_api.py

import requests
import time

class VerkadaClient:
    def __init__(self, api_key: str, region: str = "US"):
        """
        :param api_key:  The top-level API Key you generated in Command.
        :param region:   'US' for https://api.verkada.com, 'EU' for https://api.eu.verkada.com.
        """
        self.api_key = api_key
        self.base_url = "https://api.verkada.com" if region == "US" else "https://api.eu.verkada.com"
        
        self._token = None
        self._token_expires_at = 0  # Store an expiration time (Unix timestamp) if you want to refresh automatically

        # Get the initial Token
        self._refresh_token()

    def _refresh_token(self):
        """
        Retrieves a new short-lived token using the top-level API Key.
        Called automatically on client initialization or token expiration.
        """
        url = f"{self.base_url}/token"
        headers = {
            "Accept": "application/json",
            "x-api-key": self.api_key
        }
        resp = requests.post(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        self._token = data["token"]

        # If you want to track expiry (currently always 30 minutes),
        # store a timestamp to know when to refresh:
        self._token_expires_at = int(time.time()) + (30 * 60)

    def _maybe_refresh_token(self):
        """
        Refresh the token if it's close to expiry.
        """
        # You could also refresh if any request fails with a 401.
        # For simplicity, we refresh automatically if we're within 2 minutes of expiry:
        if time.time() >= (self._token_expires_at - 120):
            self._refresh_token()

    def _headers(self):
        """
        Returns the standard headers needed for any VAPI request.
        """
        self._maybe_refresh_token()
        return {
            "Accept": "application/json",
            "x-verkada-auth": self._token
        }

    # -----------------------------
    # Example convenience methods
    # -----------------------------
    
    def get_camera_alerts(self):
        """
        Example GET request to retrieve camera alerts.
        """
        url = f"{self.base_url}/cameras/v1/alerts"
        resp = requests.get(url, headers=self._headers(), timeout=15)
        resp.raise_for_status()
        return resp.json()

    def list_devices(self):
        """
        Example of listing devices (assuming your environment has the correct endpoint).
        """
        url = f"{self.base_url}/cameras/v1/devices"
        resp = requests.get(url, headers=self._headers(), timeout=15)
        resp.raise_for_status()
        return resp.json()

    # Add other calls, e.g. to Alarms, Access, etc.
    # def get_alarms(...):
    #     ...
