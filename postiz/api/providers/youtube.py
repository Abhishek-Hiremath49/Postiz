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

import frappe
import requests
import os
from datetime import datetime, timedelta


class YouTubeProvider:
    def __init__(self, account, channel):
        self.account = account
        self.channel = channel

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
            raise Exception(f"Token refresh failed: {token.get('error_description')}")

        self.account.access_token = token["access_token"]
        self.account.expires_at = datetime.now() + timedelta(
            seconds=token["expires_in"]
        )
        self.account.save(ignore_permissions=True)
        frappe.db.commit()

    def post(self, row, media_path=None):
        # YouTube REQUIRES a video file
        if not media_path or not os.path.exists(media_path):
            raise Exception("YouTube requires a video file to upload")

        # Refresh token if needed
        if self.account.expires_at < datetime.now():
            self.refresh_token()

        headers = {"Authorization": f"Bearer {self.account.access_token}"}

        snippet = {
            "title": row.title or "Untitled",
            "description": row.content or "",
            "tags": [t.strip() for t in (row.tags or "").split(",") if t.strip()],
        }
        status = {
            "privacyStatus": (row.type or "public").lower(),
            "selfDeclaredMadeForKids": row.made_for_kids == "Yes",
        }

        metadata = {"snippet": snippet, "status": status}

        # Initiate resumable upload
        init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
        init_res = requests.post(
            init_url,
            json=metadata,
            headers={**headers, "Content-Type": "application/json; charset=UTF-8"},
        )
        if init_res.status_code != 200:
            raise Exception(f"YouTube init failed: {init_res.text}")

        upload_url = init_res.headers["Location"]

        # Upload file
        chunk_size = 256 * 1024
        file_size = os.path.getsize(media_path)
        bytes_sent = 0

        with open(media_path, "rb") as f:
            while bytes_sent < file_size:
                chunk = f.read(chunk_size)
                content_range = (
                    f"bytes {bytes_sent}-{bytes_sent + len(chunk) - 1}/{file_size}"
                )
                res = requests.put(
                    upload_url,
                    data=chunk,
                    headers={
                        **headers,
                        "Content-Length": str(len(chunk)),
                        "Content-Range": content_range,
                    },
                )
                if res.status_code in (200, 201):
                    return res
                if res.status_code != 308:
                    raise Exception(f"YouTube upload failed: {res.text}")
                bytes_sent = (
                    int(res.headers.get("Range", f"0-{bytes_sent}").split("-")[1]) + 1
                )

        return res
