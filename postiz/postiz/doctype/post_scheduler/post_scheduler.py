# Copyright (c) 2025, Abhishek and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import json
import requests
import frappe


class PostScheduler(Document):
    pass


@frappe.whitelist()
def call_fastapi(doc, method):
    url = "https://localhost:5000/api/public/v1/integrations"

    payload = {
        "channel": doc.channel,
        "description": doc.description,
    }

    try:
        res = requests.post(
            url, data=json.dumps(payload), headers={"Content-Type": "application/json"}
        )
        frappe.logger().info(f"FASTAPI RESPONSE: {res.text}")
    except Exception as e:
        frappe.logger().error(f"ERROR CALLING FASTAPI: {str(e)}")
