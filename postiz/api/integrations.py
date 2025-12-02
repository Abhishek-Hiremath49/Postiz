import frappe
import requests
from frappe import _


@frappe.whitelist()
def fetch_postiz_integrations():
    """
    Fetch list of connected integrations (channels) from Postiz.
    Endpoint: GET /public/v1/integrations
    """
    try:
        settings = frappe.get_single("Social Media Settings")
        api_key = settings.get_password("api_key")

        url = "http://localhost:5000/api/public/v1/integrations"
        headers = {"Authorization": api_key, "Content-Type": "application/json"}

        response = requests.get(url, headers=headers, timeout=30)
        data = response.json()

        if response.status_code != 200:
            frappe.throw(_("Failed to fetch integrations: {0}").format(response.text))

        return {"success": True, "integrations": data.get("integrations", [])}

    except Exception as e:
        frappe.log_error(f"Integration fetch error: {str(e)}")
        return {"success": False, "message": str(e)}
