# import json
# import frappe
# import requests
# from frappe import _
# from datetime import timedelta


# # For self-hosted Postiz UI on http://localhost:5000
# # Public API base is {BACKEND_URL}/public/v1 according to docs

# POSTIZ_PUBLIC_BASE = "http://localhost:5000/api/public/v1"
# POSTIZ_POSTS_URL = f"{POSTIZ_PUBLIC_BASE}/posts"

# # Api Key Handling
# def _get_api_key_and_timeout():
#     """Read API key + timeout from Social Media Settings."""
#     settings = frappe.get_single("Social Media Settings")
#     api_key = settings.get_password("api_key")

#     if not api_key:
#         frappe.throw(_("Postiz API key is not configured in Social Media Settings."))

#     timeout = settings.api_timeout_seconds or 30
#     return api_key, timeout

# # Build Postiz API payload
# def _build_postiz_payload(post):

#     # Build posts using child table
#     posts_payload = []

#     for row in post.platforms:
#         if not row.is_enabled:
#             continue

#         if not row.content:
#             frappe.throw(
#                 _("Content is missing in platform row: {0}").format(row.platforms)
#             )

#         if not row.integration_id:
#             frappe.throw(
#                 _("Integration ID missing for platform: {0}").format(row.platforms)
#             )

#         posts_payload.append(
#             {
#                 "integration": {"id": row.integration_id},
#                 "value": [
#                     {
#                         "content": row.content,
#                         "image": [
#                             {
#                                 "id": frappe.generate_hash(length=16),
#                                 "path": row.media,
#                             }
#                         ],
#                     }
#                 ],
#                 "settings": {
#                     "title": post.title,
#                     "type": "public",
#                     "who_can_reply_post": "everyone",
#                 },
#             }
#         )

#     if not posts_payload:
#         frappe.throw(_("No enabled platforms with content found."))

#     schedule_time = post.scheduled_time.strftime("%Y-%m-%dT%H:%M:%S+05:30")

#     payload = {
#         "type": "schedule",
#         "date": schedule_time,
#         "shortLink": False,
#         "tags": [],
#         "posts": posts_payload,
#     }

#     return payload

# # Schedule Post API calls
# @frappe.whitelist()
# def schedule_post(post_id):
#     """
#     Called from the Social Media Post form.
#     Creates a scheduled post in Postiz via the Public API
#     and updates the ERPNext document accordingly.
#     """
#     try:
#         post = frappe.get_doc("Social Media Post", post_id)

#         if post.status != "Draft":
#             return {
#                 "success": False,
#                 "message": _("Post must be in Draft status to schedule."),
#             }

#         # Set status to Scheduling
#         post.status = "Scheduling"
#         post.error_message = None
#         post.api_response = None
#         post.save(ignore_permissions=True)
#         frappe.db.commit()

#         result = make_schedule_api_call(post)

#         if result["success"]:
#             post.status = "Scheduled"
#             post.external_post_id = result.get("external_post_id")
#             post.scheduled_at = frappe.utils.now()
#             post.api_response = json.dumps(result.get("response_data", {}), indent=2)
#             post.error_message = None
#             message = _("Post scheduled successfully in Postiz.")
#         else:
#             post.status = "Schedule Failed"
#             # post.error_message = result.get("error_message")
#             err = result.get("error_message")
#             if isinstance(err, (list, dict)):
#                 err = json.dumps(err, indent=2)
#                 post.error_message = err or "Unknown error"
#             post.api_response = json.dumps(result.get("response_data", {}), indent=2)
#             message = result.get("error_message", "Failed to schedule post.")

#         post.save(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "success": result["success"],
#             "message": message,
#             "post_id": post_id,
#             "status": post.status,
#             "external_post_id": post.external_post_id if result["success"] else None,
#         }

#     except Exception as e:
#         # frappe.log_error(f"Error in schedule_post: {frappe.get_traceback()}")
#         frappe.log_error(title="Postiz API Error", message=frappe.get_traceback())
#         # best-effort mark as failed
#         try:
#             post = frappe.get_doc("Social Media Post", post_id)
#             post.status = "Schedule Failed"
#             post.error_message = str(e)
#             post.save(ignore_permissions=True)
#             frappe.db.commit()
#         except Exception:
#             pass

#         return {"success": False, "message": str(e)}


# def make_schedule_api_call(post):
#     """
#     Low-level API call to POST /public/v1/posts on Postiz.
#     Returns dict: {success, external_post_id, response_data, error_message}
#     """
#     try:
#         api_key, timeout = _get_api_key_and_timeout()
#         payload = _build_postiz_payload(post)

#         headers = {
#             # IMPORTANT: Postiz expects raw API key, not "Bearer x"
#             "Authorization": api_key,
#             "Content-Type": "application/json",
#         }

#         # Log request for debugging
#         frappe.log_error(
#             f"Postiz API Request:\nURL: {POSTIZ_POSTS_URL}\nPayload:\n{json.dumps(payload, indent=2)}",
#             "Postiz API Request",
#         )

#         response = requests.post(
#             POSTIZ_POSTS_URL,
#             json=payload,
#             headers=headers,
#             timeout=timeout,
#         )

#         try:
#             response_data = response.json()  # if response.text else {}
#         except Exception:
#             response_data = {"raw_response": response.text}

#         if response.status_code in (200, 201):

#             external_post_id = None

#             # Postiz returns: [ { postId, integration } ]
#             if isinstance(response_data, list) and len(response_data) > 0:
#                 external_post_id = response_data[0].get("postId")

#             # Postiz also sometimes returns object:
#             if isinstance(response_data, dict):
#                 external_post_id = response_data.get("postId") or response_data.get(
#                     "data", {}
#                 ).get("id")

#             return {
#                 "success": True,
#                 "external_post_id": external_post_id,
#                 "response_data": response_data,
#             }

#         error_message = (
#             response_data.get("message")
#             if isinstance(response_data, dict)
#             else response.text
#         )
#         # Convert list/dict to string to prevent Frappe validation error
#         if isinstance(error_message, (list, dict)):
#             error_message = json.dumps(error_message, indent=2)

#         return {
#             "success": False,
#             "error_message": error_message,
#             "response_data": response_data,
#         }

#     except requests.exceptions.Timeout:
#         return {
#             "success": False,
#             "error_message": _("Postiz API request timed out."),
#             "response_data": {},
#         }
#     except requests.exceptions.ConnectionError:
#         return {
#             "success": False,
#             "error_message": _(
#                 "Could not connect to Postiz API (check localhost:5000)."
#             ),
#             "response_data": {},
#         }
#     except requests.exceptions.RequestException as e:
#         return {
#             "success": False,
#             "error_message": f"Postiz API request failed: {str(e)}",
#             "response_data": {},
#         }
#     except Exception as e:
#         frappe.log_error(
#             f"Unexpected error in Postiz API call: {frappe.get_traceback()}"
#         )
#         return {
#             "success": False,
#             "error_message": f"Unexpected error: {str(e)}",
#             "response_data": {},
#         }

# # Post Status
# @frappe.whitelist()
# def get_post_status(post_id):
#     """
#     Simple helper to return local status from Frappe.
#     (Does not call Postiz; use refresh_post_status_from_api for that.)
#     """
#     try:
#         post = frappe.get_doc("Social Media Post", post_id)
#         return {
#             "success": True,
#             "post_id": post_id,
#             "status": post.status,
#             "external_post_id": post.external_post_id,
#             "error_message": post.error_message,
#             "scheduled_at": post.scheduled_at,
#         }
#     except Exception as e:
#         return {"success": False, "message": str(e)}

# # Cancel Scheduled Post
# @frappe.whitelist()
# def cancel_scheduled_post(post_id):
#     """
#     Cancel a scheduled post in Postiz (and mark as Cancelled in ERPNext).
#     Uses DELETE /public/v1/posts/:id
#     """
#     try:
#         post = frappe.get_doc("Social Media Post", post_id)

#         if post.status != "Scheduled":
#             return {
#                 "success": False,
#                 "message": _("Only scheduled posts can be cancelled."),
#             }

#         if not post.external_post_id:
#             # Allow local-only cancel if for some reason we don't have Postiz ID
#             post.status = "Cancelled"
#             post.error_message = _("Cancelled locally - no external Postiz post ID.")
#             post.save(ignore_permissions=True)
#             frappe.db.commit()
#             return {
#                 "success": True,
#                 "message": _("Post marked as Cancelled locally (no Postiz ID)."),
#             }

#         api_key, timeout = _get_api_key_and_timeout()

#         url = f"{POSTIZ_POSTS_URL}/{post.external_post_id}"
#         headers = {
#             "Authorization": api_key,
#             "Content-Type": "application/json",
#         }

#         response = requests.delete(url, headers=headers, timeout=timeout)

#         # Docs: DELETE /public/v1/posts/:id returns { "id": "..." }
#         if response.status_code in (200, 204):
#             post.status = "Cancelled"
#             post.save(ignore_permissions=True)
#             frappe.db.commit()
#             return {
#                 "success": True,
#                 "message": _("Post cancelled successfully in Postiz."),
#             }
#         elif response.status_code == 404:
#             # Not found in Postiz => still cancel locally
#             post.status = "Cancelled"
#             post.error_message = _("Post not found in Postiz; cancelled locally.")
#             post.save(ignore_permissions=True)
#             frappe.db.commit()
#             return {
#                 "success": True,
#                 "message": _("Post not found in Postiz; cancelled locally."),
#             }
#         else:
#             return {
#                 "success": False,
#                 "message": f"Failed to cancel in Postiz: {response.text}",
#             }

#     except Exception as e:
#         frappe.log_error(f"Error cancelling post in Postiz: {frappe.get_traceback()}")
#         return {"success": False, "message": str(e)}

# # Refresh Post Status
# @frappe.whitelist()
# def refresh_post_status_from_api(post_id):
#     """
#     Fetch latest status from Postiz using the public 'Post list' endpoint:
#     GET /public/v1/posts?startDate=...&endDate=...

#     We search a small window around the scheduled time and match by ID.
#     """
#     try:
#         post = frappe.get_doc("Social Media Post", post_id)

#         if not post.external_post_id:
#             return {"success": False, "message": _("No external Postiz post ID found.")}

#         api_key, timeout = _get_api_key_and_timeout()

#         # Choose a 1-day window around scheduled_time (or around now as fallback)
#         base_dt = post.scheduled_time or frappe.utils.now_datetime()
#         start = (base_dt - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
#         end = (base_dt + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

#         params = {"startDate": start, "endDate": end}

#         headers = {
#             "Authorization": api_key,
#             "Content-Type": "application/json",
#         }

#         response = requests.get(
#             POSTIZ_POSTS_URL, headers=headers, params=params, timeout=timeout
#         )

#         data = response.json() if response.text else {}

#         if response.status_code != 200:
#             return {
#                 "success": False,
#                 "message": f"Failed to fetch status from Postiz: {response.text}",
#             }

#         # Docs: response = { "posts": [ { "id", "content", "publishDate", "state", "integration": {...} } ] }
#         target = None
#         for item in data.get("posts", []):
#             if item.get("id") == post.external_post_id:
#                 target = item
#                 break

#         if not target:
#             return {
#                 "success": False,
#                 "message": _("Post not found in Postiz list for selected window."),
#             }

#         state = (target.get("state") or "").upper()

#         if state == "QUEUE":
#             post.status = "Scheduled"
#         elif state == "PUBLISHED":
#             post.status = "Published"
#             post.published_at = target.get("publishDate")
#         elif state == "ERROR":
#             post.status = "Schedule Failed"
#             post.error_message = _("Postiz status: ERROR")
#         elif state == "DRAFT":
#             post.status = "Draft"

#         post.api_response = json.dumps(target, indent=2)
#         post.save(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "success": True,
#             "message": _("Status updated from Postiz."),
#             "status": post.status,
#             "data": target,
#         }

#     except Exception as e:
#         frappe.log_error(f"Error refreshing Postiz status: {frappe.get_traceback()}")
#         return {"success": False, "message": str(e)}

# import frappe
# from frappe.utils import now_datetime
# from datetime import datetime

# def execute_scheduled_posts():
#     """
#     Called by scheduler (hooks.py). Finds posts with status Scheduled and time <= now.
#     For each platform row, if an account link exists we post directly using provider.
#     """
#     posts = frappe.get_all("Social Media Post",
#                            filters=[["status", "=", "Scheduled"], ["scheduled_time", "<=", now_datetime()]],
#                            fields=["name"])
#     for p in posts:
#         try:
#             doc = frappe.get_doc("Social Media Post", p.name)
#             for row in doc.platforms:
#                 # row is a child table row of type Social Media Platform (child)
#                 # we expect new field 'account' to exist (Link to Social Media Account)
#                 if not row.is_enabled:
#                     continue

#                 if not row.account:
#                     # mark error for this row
#                     frappe.log_error(f"No connected account selected for platform row in post {doc.name}", "Scheduler Error")
#                     continue

#                 account = frappe.get_doc("Social Media Account", row.account)
#                 channel = frappe.get_doc("Channel", account.channel)

#                 res = provider.post(row.content, media=row.media)

#                 # Save API response and external_post_id if available
#                 try:
#                     resp_text = res.text
#                 except Exception:
#                     resp_text = str(res)

#                 # record the response in post doc fields
#                 doc.api_response = (doc.api_response or "") + f"\n\nPlatform {row.platforms} response:\n{resp_text}"
#                 if res.status_code in (200,201):
#                     # try to capture id
#                     try:
#                         j = res.json()
#                         external_id = j.get("data", {}).get("id") or j.get("id")
#                         doc.external_post_id = external_id or doc.external_post_id
#                     except Exception:
#                         pass
#                 else:
#                     doc.error_message = (doc.error_message or "") + f"\n{row.platforms}: {res.text}"

#             doc.status = "Published"
#             doc.save(ignore_permissions=True)
#         except Exception as e:
#             frappe.log_error(f"Error posting scheduled post {p.name}: {frappe.get_traceback()}")

# @frappe.whitelist()
# def manual_schedule(post_id):
#     """
#     Called from UI to trigger schedule_post logic synchronously (or mark Scheduling).
#     """
#     post = frappe.get_doc("Social Media Post", post_id)
#     if post.status != "Draft":
#         return {"success": False, "message": "Only Draft posts can be scheduled."}
#     post.status = "Scheduled"
#     post.save(ignore_permissions=True)
#     frappe.db.commit()
#     return {"success": True, "message": "Post marked as Scheduled. Scheduler will run soon."}

# import frappe
# from frappe.utils import now_datetime
# from postiz.api.providers.youtube import YouTubeProvider  # Import your provider


# @frappe.whitelist()
# def manual_schedule(post_id):
#     """
#     Called from UI to trigger schedule_post logic synchronously (or mark Scheduling).
#     """
#     post = frappe.get_doc("Social Media Post", post_id)
#     if post.status != "Draft":
#         return {"success": False, "message": "Only Draft posts can be scheduled."}
#     post.status = "Scheduled"
#     post.save(ignore_permissions=True)
#     frappe.db.commit()
#     return {
#         "success": True,
#         "message": "Post marked as Scheduled. Scheduler will run soon.",
#     }


# def publish_scheduled_posts():
#     """
#     Called by scheduler (hooks.py). Finds posts with status Scheduled and time <= now.
#     For each platform row, if an account link exists we post directly using provider.
#     """
#     posts = frappe.get_all(
#         "Social Media Post",
#         filters=[
#             ["status", "=", "Scheduled"],
#             ["scheduled_time", "<=", now_datetime()],
#         ],
#         fields=["name"],
#     )
#     for p in posts:
#         try:
#             doc = frappe.get_doc("Social Media Post", p.name)
#             for row in doc.platforms:
#                 if not row.is_enabled:
#                     continue

#                 if not row.account:
#                     frappe.log_error(
#                         f"No connected account selected for platform row in post {doc.name}",
#                         "Scheduler Error",
#                     )
#                     continue

#                 account = frappe.get_doc("Social Media Account", row.account)
#                 channel = frappe.get_doc("Channel", account.channel)

#                 # Select provider based on channel
#                 if channel.channel_name == "YouTube":
#                     provider = YouTubeProvider(account, channel)
#                 else:
#                     continue  # Skip if no provider

#                 res = provider.post(row.content, row.media)

#                 # Save API response and external_post_id if available
#                 resp_text = res.text if hasattr(res, "text") else str(res)
#                 doc.api_response = (
#                     doc.api_response or ""
#                 ) + f"\n\nPlatform {row.platforms} response:\n{resp_text}"

#                 if res.status_code in (200, 201):
#                     try:
#                         j = res.json()
#                         external_id = j.get("id") or j.get("data", {}).get("id")
#                         doc.external_post_id = external_id or doc.external_post_id
#                     except Exception:
#                         pass
#                 else:
#                     doc.error_message = (
#                         doc.error_message or ""
#                     ) + f"\n{row.platforms}: {res.text}"

#             doc.status = "Published"
#             doc.save(ignore_permissions=True)
#         except Exception as e:
#             frappe.log_error(
#                 f"Error posting scheduled post {p.name}: {frappe.get_traceback()}"
#             )

# postiz/postiz/api/post_scheduler.py


import frappe
import os
from frappe.utils import now_datetime
from frappe.utils.file_manager import get_file_path

from postiz.api.providers.youtube import YouTubeProvider
from postiz.api.providers.facebook import FacebookProvider


@frappe.whitelist()
def post_now(post_id):
    try:
        post = frappe.get_doc("Social Media Post", post_id)

        for row in post.platforms:
            if not row.is_enabled or not row.accounts:
                continue

            account = frappe.get_doc("Social Media Account", row.accounts)
            channel = frappe.get_doc("Channel", account.channel)

            # ——— GET REAL FILE PATH SAFELY (public or private) ———
            media_path = None
            if row.media:
                relative_path = get_file_path(row.media)
                if relative_path:
                    # Public files
                    candidate = frappe.get_site_path(
                        "public", relative_path.lstrip("/")
                    )
                    if os.path.exists(candidate):
                        media_path = candidate
                    else:
                        # Private files
                        candidate = frappe.get_site_path(
                            "private", relative_path.lstrip("/")
                        )
                        if os.path.exists(candidate):
                            media_path = candidate

            # ——— SELECT PROVIDER ———
            if channel.channel_name == "YouTube":
                if not media_path or not os.path.exists(media_path):
                    continue
                provider = YouTubeProvider(account, channel)
            elif channel.channel_name == "Facebook":
                provider = FacebookProvider(account, channel)
            else:
                continue

            # ——— POST ———
            response = provider.post(row, media_path)

            if response and response.status_code in (200, 201):
                result = response.json()

                if channel.channel_name == "Facebook":
                    fb_post_id = result.get("id") or result.get("post_id")
                    fb_url = f"https://www.facebook.com/{fb_post_id}"
                    frappe.db.set_value(
                        "Social Media Post",
                        post.name,
                        {
                            "status": "Published",
                            "facebook_post_id": fb_post_id,
                            "facebook_url": fb_url,
                            "api_response": frappe.as_json(result),
                            "error_message": None,
                        },
                    )

                elif channel.channel_name == "YouTube":
                    video_id = result.get("id")
                    video_url = f"https://youtu.be/{video_id}"
                    frappe.db.set_value(
                        "Social Media Post",
                        post.name,
                        {
                            "status": "Published",
                            "youtube_video_id": video_id,
                            "youtube_url": video_url,
                            "api_response": frappe.as_json(result),
                            "error_message": None,
                        },
                    )

                frappe.db.commit()
                return {"success": True, "message": "Posted successfully!"}

            else:
                error_msg = response.text[:500] if response else "No response"
                frappe.db.set_value(
                    "Social Media Post",
                    post.name,
                    {"status": "Failed", "error_message": error_msg},
                )
                frappe.db.commit()
                return {"success": False, "error": error_msg}

        return {"success": False, "error": "No enabled platform found"}

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(), title=f"Post Failed: {post_id}"
        )
        frappe.db.set_value(
            "Social Media Post",
            post_id,
            {"status": "Failed", "error_message": str(e)[:500]},
        )
        frappe.db.commit()
        return {"success": False, "error": str(e)}


def publish_due_posts():
    now = now_datetime()
    posts = frappe.get_all(
        "Social Media Post",
        filters={"status": "Scheduled", "scheduled_time": ["<=", now], "docstatus": 1},
        fields=["name"],
    )

    for p in posts:
        try:
            frappe.call("postiz.api.post_scheduler.post_now", post_id=p.name)
            frappe.db.commit()
        except:
            frappe.db.rollback()
