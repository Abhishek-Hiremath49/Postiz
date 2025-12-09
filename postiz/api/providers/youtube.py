# import requests
# import frappe
# from datetime import datetime, timedelta
# from .base import BaseProvider


# class YouTubeProvider(BaseProvider):

#     def refresh_token(self):
#         ch = self.channel
#         data = {
#             "client_id": ch.oauth_client_id,
#             "client_secret": ch.oauth_client_secret,
#             "grant_type": "refresh_token",
#             "refresh_token": self.account.refresh_token,
#         }

#         r = requests.post(ch.token_url, data=data)
#         token = r.json()

#         self.account.access_token = token["access_token"]
#         self.account.expires_at = datetime.utcnow() + timedelta(
#             seconds=token["expires_in"]
#         )
#         self.account.save(ignore_permissions=True)
#         frappe.db.commit()

#     def post(self, content, media_path):
#         # Upload video to YouTube
#         headers = {"Authorization": f"Bearer {self.account.access_token}"}

#         metadata = {
#             "snippet": {
#                 "title": content,
#                 "description": content,
#                 "tags": ["frappe", "postiz"],
#             },
#             "status": {"privacyStatus": "public"},
#         }

#         # Two-step upload (init + upload)
#         init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
#         init_headers = {**headers, "Content-Type": "application/json; charset=UTF-8"}
#         init_res = requests.post(init_url, json=metadata, headers=init_headers)

#         upload_url = init_res.headers["Location"]

#         with open(media_path, "rb") as f:
#             video_data = f.read()

#         upload_headers = {
#             **headers,
#             "Content-Length": str(len(video_data)),
#             "Content-Type": "video/*",
#         }

#         return requests.put(upload_url, data=video_data, headers=upload_headers)
# import requests
# import frappe
# from datetime import datetime, timedelta
# import os
# from frappe.utils import get_files_path


# class BaseProvider:
#     def __init__(self, account, channel):
#         self.account = account
#         self.channel = channel


# class YouTubeProvider(BaseProvider):
#     def refresh_token(self):
#         settings = frappe.get_single("Social Media Settings")
#         data = {
#             "client_id": settings.youtube_client_id,
#             "client_secret": settings.youtube_client_secret,
#             "grant_type": "refresh_token",
#             "refresh_token": self.account.refresh_token,
#         }

#         r = requests.post(self.channel.token_url, data=data)
#         token = r.json()

#         if "error" in token:
#             raise Exception(f"Token refresh failed: {token['error_description']}")

#         self.account.access_token = token["access_token"]
#         self.account.expires_at = datetime.now() + timedelta(
#             seconds=token["expires_in"]
#         )
#         self.account.save(ignore_permissions=True)
#         frappe.db.commit()

#     def post(self, content, media_path):
#         # Full path to media (Frappe file)
#         full_media_path = os.path.join(get_files_path(), media_path.lstrip("/files/"))

#         # Refresh if expired
#         if self.account.expires_at < datetime.now():
#             self.refresh_token()

#         headers = {"Authorization": f"Bearer {self.account.access_token}"}

#         metadata = {
#             "snippet": {
#                 "title": content,
#                 "description": content,
#                 "tags": ["frappe", "postiz"],
#             },
#             "status": {"privacyStatus": "public"},
#         }

#         # Initiate resumable upload
#         init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
#         init_headers = {**headers, "Content-Type": "application/json; charset=UTF-8"}
#         init_res = requests.post(init_url, json=metadata, headers=init_headers)

#         if init_res.status_code != 200:
#             raise Exception(f"Upload init failed: {init_res.text}")

#         upload_url = init_res.headers["Location"]

#         # Upload video in chunks (resumable)
#         chunk_size = 256 * 1024  # 256KB
#         file_size = os.path.getsize(full_media_path)
#         bytes_sent = 0

#         with open(full_media_path, "rb") as f:
#             while bytes_sent < file_size:
#                 chunk = f.read(chunk_size)
#                 content_range = (
#                     f"bytes {bytes_sent}-{bytes_sent + len(chunk) - 1}/{file_size}"
#                 )
#                 upload_headers = {
#                     **headers,
#                     "Content-Length": str(len(chunk)),
#                     "Content-Range": content_range,
#                 }
#                 res = requests.put(upload_url, data=chunk, headers=upload_headers)

#                 if res.status_code in (200, 201):
#                     return res  # Success
#                 elif res.status_code != 308:  # 308 = resume incomplete
#                     raise Exception(f"Upload failed: {res.text}")

#                 # Update bytes_sent from response (if partial)
#                 bytes_sent = (
#                     int(res.headers.get("Range", f"bytes=0-{bytes_sent}").split("-")[1])
#                     + 1
#                 )

#         return res

import requests
import frappe
from datetime import datetime, timedelta
import os
from frappe.utils.file_manager import get_file_path


class BaseProvider:
    def __init__(self, account, channel):
        self.account = account
        self.channel = channel


class YouTubeProvider(BaseProvider):
    def refresh_token(self):
        settings = frappe.get_single("Social Media Settings")
        data = {
            "client_id": settings.youtube_client_id,
            "client_secret": settings.youtube_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.account.refresh_token,
        }
        r = requests.post(self.channel.token_url, data=data)
        token = r.json()
        if "error" in token:
            raise Exception(f"Token refresh failed: {token['error_description']}")
        self.account.access_token = token["access_token"]
        self.account.expires_at = datetime.now() + timedelta(
            seconds=token["expires_in"]
        )
        self.account.save(ignore_permissions=True)
        frappe.db.commit()

    def post(
        self, content, media_path
    ):  # `content` is now the Social Media Platform doc
        # Quick enable check from your fields
        if not content.is_enabled:
            frappe.msgprint("Post skipped: Platform is not enabled.")
            return None

        full_media_path = media_path  # ← CORRECT WAY

        if not os.path.exists(full_media_path):
            raise Exception(f"Media file not found on disk: {full_media_path}")

        # Refresh if expired
        if self.account.expires_at < datetime.now():
            self.refresh_token()

        headers = {"Authorization": f"Bearer {self.account.access_token}"}

        # Build payload from your fields (matches YouTube Videos.insert structure)
        snippet = {
            "title": content.title or "Untitled Video",  # From 'title' field (required)
            "description": content.content or "",  # From 'content' Long Text field
            "tags": [
                tag.strip() for tag in (content.tags or "").split(",") if tag.strip()
            ],  # From 'tags' Data field (comma-separated)
        }

        status = {
            "privacyStatus": content.type.lower()
            or "public",  # Default; add a field later to make dynamic (e.g., Select: public/unlisted/private)
            "selfDeclaredMadeForKids": content.made_for_kids
            == "Yes",  # From 'made_for_kids' Select field (Yes/No)
        }

        # Thumbnail handling: Not supported in insert (auto-generated by YouTube)
        # if content.thumbnail:  # From 'thumbnail' Attach Image field
        #     frappe.msgprint(
        #         "Note: Custom thumbnails are auto-generated by YouTube after upload. Use thumbnails.set API for custom ones later."
        #     )

        metadata = {
            "snippet": snippet,
            "status": status,
        }

        # Initiate resumable upload (using your Channel's base + endpoint would be even better!)
        # For now, hard-coded as before; refactor to: init_url = self.channel.api_base_url + self.channel.post_endpoint
        init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"  # self.channel.api_base_url + self.channel.post_endpoint
        init_headers = {**headers, "Content-Type": "application/json; charset=UTF-8"}
        init_res = requests.post(init_url, json=metadata, headers=init_headers)
        if init_res.status_code != 200:
            raise Exception(f"Upload init failed: {init_res.text}")

        upload_url = init_res.headers["Location"]

        # Upload video in chunks (resumable) - unchanged
        chunk_size = 256 * 1024  # 256KB
        file_size = os.path.getsize(full_media_path)
        bytes_sent = 0
        with open(full_media_path, "rb") as f:
            while bytes_sent < file_size:
                chunk = f.read(chunk_size)
                content_range = (
                    f"bytes {bytes_sent}-{bytes_sent + len(chunk) - 1}/{file_size}"
                )
                upload_headers = {
                    **headers,
                    "Content-Length": str(len(chunk)),
                    "Content-Range": content_range,
                }
                res = requests.put(upload_url, data=chunk, headers=upload_headers)
                if res.status_code in (200, 201):
                    return res  # Success - returns video details
                elif res.status_code != 308:  # 308 = resume incomplete
                    raise Exception(f"Upload failed: {res.text}")
                # Update bytes_sent from response (if partial)
                bytes_sent = (
                    int(res.headers.get("Range", f"bytes=0-{bytes_sent}").split("-")[1])
                    + 1
                )

        return res
