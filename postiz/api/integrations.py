import frappe
import requests
from frappe import _


# @frappe.whitelist()
# def fetch_postiz_integrations():
#     """
#     Fetch list of connected integrations (channels) from Postiz.
#     Endpoint: GET /public/v1/integrations
#     """
#     try:
#         settings = frappe.get_single("Social Media Settings")
#         api_key = settings.get_password("api_key")

#         url = "http://localhost:5000/api/public/v1/integrations"
#         headers = {"Authorization": api_key, "Content-Type": "application/json"}

#         response = requests.get(url, headers=headers, timeout=30)
#         data = response.json()

#         if response.status_code != 200:
#             frappe.throw(_("Failed to fetch integrations: {0}").format(response.text))

#         return {"success": True, "integrations": data.get("integrations", [])}


#     except Exception as e:
#         frappe.log_error(f"Integration fetch error: {str(e)}")
#         return {"success": False, "message": str(e)}


# @frappe.whitelist()
# def get_integration_by_platform(platform):
#     """
#     Fetch integration from Postiz matching selected platform.
#     Example: platform='X' → identifier='X'
#     """
#     settings = frappe.get_single("Social Media Settings")
#     api_key = settings.get_password("api_key")

#     url = "http://localhost:5000/api/public/v1/integrations"
#     headers = {"Authorization": api_key}

#     response = requests.get(url, headers=headers, timeout=20)
#     data = response.json()

#     # In your API, response is a LIST
#     integrations = data if isinstance(data, list) else data.get("integrations", [])

#     for item in integrations:
#         # Match platform by identifier (case-insensitive)
#         if item.get("identifier", "").lower() == platform.lower():
#             return {
#                 "integration_id": item.get("id"),
#                 # "profile": item.get("profile"),
#                 # "name": item.get("name"),
#             }

#     return {"integration_id": None}

# import frappe
# from frappe import _

# @frappe.whitelist()
# def get_integration_by_platform(platform):
#     """
#     Fetch connected account from Social Media Account matching platform (channel).
#     """
#     accounts = frappe.get_all("Social Media Account",
#                               filters={"channel": platform, "connected": 1},
#                               fields=["name"])

#     if accounts:
#         return {"integration_id": accounts[0].name}  # Use account name as ID
#     return {"integration_id": None}
