import frappe
import requests
import urllib.parse
from frappe.utils import get_request_site_address
import hashlib
import os


@frappe.whitelist()
def start(channel):
    """Start OAuth2 flow for any platform"""
    ch = frappe.get_doc("Channel", channel)

    redirect_uri = get_request_site_address() + "/api/method/postiz.api.oauth.callback"
    state = "af12gst"  #hashlib.sha256(os.urandom(1024)).hexdigest()
    frappe.cache().set_value(f"oauth_state:{state}", channel, expires_in_sec=3000)

    # For YouTube, use global settings for client_id (not per channel)
    settings = frappe.get_single("Social Media Settings")
    client_id = (
        settings.youtube_client_id if channel == "YouTube" else ch.oauth_client_id
    )
    SCOPES = ch.scopes
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "access_type": "offline",
        "scope": SCOPES,
        "state": state,
        "prompt": "consent",
    }

    auth_url = f"{ch.authorization_url}?{urllib.parse.urlencode(params)}"

    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = auth_url


# @frappe.whitelist(allow_guest=True)
# def callback(code, state):
#     """Handles OAuth2 callback and stores account"""
#     if not code or not state:
#         frappe.throw("Missing code or state")

#     channel_name = frappe.cache().get_value(f"oauth_state:{state}")
#     if not channel_name:
#         frappe.throw("Invalid or expired OAuth state")

#     ch = frappe.get_doc("Channel", channel_name)
#     redirect_uri = get_request_site_address() + "/api/method/postiz.api.oauth.callback"

#     # Get credentials (YouTube uses global ones from Settings)
#     settings = frappe.get_single("Social Media Settings")
#     if ch.channel_name == "YouTube":
#         client_id = settings.get("youtube_client_id")
#         client_secret = settings.get("youtube_client_secret")
#     else:
#         client_id = ch.oauth_client_id
#         client_secret = ch.oauth_client_secret

#     print(client_id, client_secret)

#     if not client_id or not client_secret:
#         frappe.throw("Client ID or Secret is missing in settings")

#     # THIS IS THE IMPORTANT PART – client_id & client_secret MUST be sent
#     data = {
#         "code": code,
#         "client_id": client_id,
#         "client_secret": client_secret,
#         "redirect_uri": redirect_uri,
#         "grant_type": "authorization_code",
#     }

#     headers = {"Accept": "application/json"}

#     r = requests.post(ch.token_url, data=data, headers=headers, timeout=30)
#     token = r.json()

#     if "error" in token:
#         frappe.throw(f"OAuth error: {token.get('error_description') or token('error')}")

#     access_token = token["access_token"]
#     refresh_token = token.get("refresh_token")
#     expires_in = token.get("expires_in", 3600)

#     # Get channel info
#     userinfo = requests.get(
#         "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
#         headers={"Authorization": f"Bearer {access_token}"},
#         timeout=30,
#     ).json()

#     if userinfo.get("error"):
#         frappe.throw(f"Failed to fetch channel: {userinfo['error']['message']}")

#     title = userinfo["items"][0]["snippet"]["title"]
#     channel_id = userinfo["items"][0]["id"]

#     # Save the connected account
#     acct = frappe.new_doc("Social Media Account")
#     acct.channel = ch.name
#     acct.user_name = title
#     acct.provider_user_id = channel_id
#     acct.access_token = access_token
#     acct.refresh_token = refresh_token or ""
#     acct.expires_at = frappe.utils.add_to_date(None, seconds=expires_in)
#     acct.connected = 1
#     acct.insert(ignore_permissions=True)

#     frappe.local.response["type"] = "redirect"
#     frappe.local.response["location"] = "/app/social-media-account"


@frappe.whitelist(allow_guest=True)
def callback(code=None, state=None):
    try:
        if not code or not state:
            frappe.throw("Missing code or state")

        channel_name = frappe.cache().get_value(f"oauth_state:{state}")
        if not channel_name:
            frappe.throw("Invalid or expired state")

        ch = frappe.get_doc("Channel", channel_name)
        redirect_uri = (
            get_request_site_address() + "/api/method/postiz.api.oauth.callback"
        )

        settings = frappe.get_single("Social Media Settings")
        if ch.channel_name == "YouTube":
            client_id = settings.get("youtube_client_id")
            client_secret = settings.get("youtube_client_secret")
        else:
            client_id = ch.oauth_client_id
            client_secret = ch.oauth_client_secret

        if not client_id or not client_secret:
            frappe.throw("Client ID/Secret missing")

        # Exchange token
        r = requests.post(
            ch.token_url,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Accept": "application/json"},
            timeout=30,
        )
        token = r.json()

        if "error" in token:
            frappe.throw(
                f"OAuth Error: {token.get('error_description') or token.get('error')}"
            )

        access_token = token["access_token"]
        refresh_token = token.get("refresh_token", "")

        userinfo = requests.get(
            "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        ).json()

        if userinfo.get("error"):
            frappe.throw(f"YouTube API Error: {userinfo['error']['message']}")

        title = userinfo["items"][0]["snippet"]["title"]
        channel_id = userinfo["items"][0]["id"]

        acct = frappe.new_doc("Social Media Account")
        acct.api_response = userinfo
        acct.channel = ch.name
        acct.user_name = title
        acct.provider_user_id = channel_id
        acct.access_token = access_token
        acct.refresh_token = refresh_token
        acct.expires_at = frappe.utils.add_to_date(
            None, seconds=token.get("expires_in", 200000)
        )
        acct.connected = 1
        acct.flags.ignore_permissions = True
        acct.flags.ignore_mandatory = True
        acct.save()  # ← This saves it
        frappe.db.commit()  # ← This makes it permanent

        # Success message
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/app/social-media-account"

    except Exception as e:
        # THIS WILL SHOW YOU THE EXACT ERROR
        frappe.log_error(frappe.get_traceback(), "YouTube OAuth Callback Failed")
        frappe.throw(f"Connection failed: {str(e)}")
