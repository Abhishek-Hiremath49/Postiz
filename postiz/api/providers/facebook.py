import frappe
import requests
import os
from frappe.utils import now_datetime, get_datetime


class FacebookProvider:
    def __init__(self, account, channel):
        self.access_token = account.access_token
        self.page_id = account.provider_user_id

    # This is the Page ID

    def post(self, row, media_path=None):
        post_doc = frappe.get_doc("Social Media Post", row.parent)
        is_scheduled = (
            post_doc.status == "Scheduled"
            and post_doc.scheduled_time
            and get_datetime(post_doc.scheduled_time) > now_datetime()
        )

        base_url = f"https://graph.facebook.com/v24.0/{self.page_id}"

        # Text-only post
        if not media_path or not os.path.exists(media_path):
            endpoint = "/feed"
            data = {
                "message": row.content or "Hi",
                "access_token": self.access_token,
                "published": "false" if is_scheduled else "true",
            }
            if is_scheduled:
                data["scheduled_publish_time"] = int(
                    get_datetime(post_doc.scheduled_time).timestamp()
                )
            files = None

        # Image post
        elif os.path.splitext(media_path)[1].lower() in [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
        ]:
            endpoint = "/photos"
            files = {"source": open(media_path, "rb")}
            data = {
                "caption": row.content or "",
                "access_token": self.access_token,
                "published": "false" if is_scheduled else "true",
            }
            if is_scheduled:
                data["scheduled_publish_time"] = int(
                    get_datetime(post_doc.scheduled_time).timestamp()
                )

        # Video post
        else:
            endpoint = "/videos"
            files = {"source": open(media_path, "rb")}
            data = {
                "description": row.content or "",
                "access_token": self.access_token,
                "published": "false" if is_scheduled else "true",
            }
            if is_scheduled:
                data["scheduled_publish_time"] = int(
                    get_datetime(post_doc.scheduled_time).timestamp()
                )

        response = requests.post(base_url + endpoint, data=data, files=files)
        return response
