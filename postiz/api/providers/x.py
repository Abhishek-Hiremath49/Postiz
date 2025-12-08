# import requests
# import frappe
# from .base import BaseProvider
# from datetime import datetime, timedelta

# class XProvider(BaseProvider):
#     """
#     Minimal provider for posting to X using OAuth2. Assumes access_token is valid.
#     """

#     def __init__(self, account_doc, channel_doc):
#         self.account = account_doc
#         self.channel = channel_doc
#         self.base = channel_doc.api_base_url.rstrip("/")

#     def post(self, content, media=None):
#         """
#         POST to /2/tweets
#         """
#         url = self.base + (self.channel.post_endpoint or "/tweets")
#         headers = {"Authorization": f"Bearer {self.account.access_token}", "Content-Type": "application/json"}
#         payload = {"text": content}
#         # For media attachments with X you must upload media separately -> omitted in minimal version.
#         r = requests.post(url, headers=headers, json=payload, timeout=20)
#         # If token expired, provider should return 401 -> we can raise to let scheduler handle refresh.
#         return r
import requests
import frappe
from datetime import datetime, timedelta
from .base import BaseProvider


class XProvider(BaseProvider):

    def __init__(self, account_doc, channel_doc):
        self.account = account_doc
        self.channel = channel_doc
        self.base = self.channel.api_base_url.rstrip("/")

    # -----------------------------
    # 1) AUTO REFRESH TOKEN
    # -----------------------------
    def refresh_access_token(self):
        if not self.account.refresh_token:
            frappe.log_error("No refresh_token available", "X Refresh Failure")
            return False

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.account.refresh_token,
            "client_id": self.channel.oauth_client_id,
        }

        try:
            resp = requests.post(self.channel.token_url, data=data, timeout=20)
            resp.raise_for_status()
            tok = resp.json()

            # Update tokens
            self.account.access_token = tok.get("access_token")
            self.account.refresh_token = tok.get(
                "refresh_token", self.account.refresh_token
            )
            expires_in = tok.get("expires_in")

            if expires_in:
                self.account.token_expires_at = (
                    datetime.utcnow() + timedelta(seconds=int(expires_in))
                ).strftime("%Y-%m-%d %H:%M:%S")

            self.account.save(ignore_permissions=True)
            frappe.db.commit()
            return True
        except Exception:
            frappe.log_error(
                f"Refresh token failed:\n{frappe.get_traceback()}", "X Token Refresh"
            )
            return False

    # -----------------------------
    # 2) POST TWEET with auto-refresh
    # -----------------------------
    def post(self, content, media=None):
        url = self.base + self.channel.post_endpoint
        headers = {
            "Authorization": f"Bearer {self.account.access_token}",
            "Content-Type": "application/json",
        }

        payload = {"text": content}
        resp = requests.post(url, headers=headers, json=payload, timeout=20)

        # Token expired → refresh → retry once
        if resp.status_code == 401:
            if self.refresh_access_token():
                headers["Authorization"] = f"Bearer {self.account.access_token}"
                resp = requests.post(url, headers=headers, json=payload, timeout=20)

        return resp
