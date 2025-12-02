import json
import frappe
import requests
from frappe import _
from datetime import timedelta


# For self-hosted Postiz UI on http://localhost:5000
# Public API base is {BACKEND_URL}/public/v1 according to docs
POSTIZ_PUBLIC_BASE = "http://localhost:5000/api/public/v1"
POSTIZ_POSTS_URL = f"{POSTIZ_PUBLIC_BASE}/posts"


def _get_api_key_and_timeout():
    """Read API key + timeout from Social Media Settings."""
    settings = frappe.get_single("Social Media Settings")
    api_key = settings.get_password("api_key")

    if not api_key:
        frappe.throw(_("Postiz API key is not configured in Social Media Settings."))

    timeout = settings.api_timeout_seconds or 30
    return api_key, timeout


def _build_postiz_payload(post):

    # Build posts using child table
    posts_payload = []

    for row in post.platforms:
        if not row.is_enabled:
            continue

        if not row.content:
            frappe.throw(
                _("Content is missing in platform row: {0}").format(row.platforms)
            )

        if not row.integration_id:
            frappe.throw(
                _("Integration ID missing for platform: {0}").format(row.platforms)
            )

        posts_payload.append(
            {
                "integration": {"id": row.integration_id},
                "value": [{"content": row.content, "image": []}],
                "settings": {
                    "title": post.title,
                    "type": "public",
                    "who_can_reply_post": "everyone",
                },
            }
        )

    if not posts_payload:
        frappe.throw(_("No enabled platforms with content found."))

    schedule_time = post.scheduled_time.strftime("%Y-%m-%dT%H:%M:%S+05:30")

    payload = {
        "type": "schedule",
        "date": schedule_time,
        "shortLink": False,
        "tags": [],
        "posts": posts_payload,
    }

    return payload


@frappe.whitelist()
def schedule_post(post_id):
    """
    Called from the Social Media Post form.
    Creates a scheduled post in Postiz via the Public API
    and updates the ERPNext document accordingly.
    """
    try:
        post = frappe.get_doc("Social Media Post", post_id)

        if post.status != "Draft":
            return {
                "success": False,
                "message": _("Post must be in Draft status to schedule."),
            }

        # Set status to Scheduling
        post.status = "Scheduling"
        post.error_message = None
        post.api_response = None
        post.save(ignore_permissions=True)
        frappe.db.commit()

        result = make_schedule_api_call(post)

        if result["success"]:
            post.status = "Scheduled"
            post.external_post_id = result.get("external_post_id")
            post.scheduled_at = frappe.utils.now()
            post.api_response = json.dumps(result.get("response_data", {}), indent=2)
            post.error_message = None
            message = _("Post scheduled successfully in Postiz.")
        else:
            post.status = "Schedule Failed"
            # post.error_message = result.get("error_message")
            err = result.get("error_message")
            if isinstance(err, (list, dict)):
                err = json.dumps(err, indent=2)
                post.error_message = err or "Unknown error"
            post.api_response = json.dumps(result.get("response_data", {}), indent=2)
            message = result.get("error_message", "Failed to schedule post.")

        post.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": result["success"],
            "message": message,
            "post_id": post_id,
            "status": post.status,
            "external_post_id": post.external_post_id if result["success"] else None,
        }

    except Exception as e:
        # frappe.log_error(f"Error in schedule_post: {frappe.get_traceback()}")
        frappe.log_error(title="Postiz API Error", message=frappe.get_traceback())
        # best-effort mark as failed
        try:
            post = frappe.get_doc("Social Media Post", post_id)
            post.status = "Schedule Failed"
            post.error_message = str(e)
            post.save(ignore_permissions=True)
            frappe.db.commit()
        except Exception:
            pass

        return {"success": False, "message": str(e)}


def make_schedule_api_call(post):
    """
    Low-level API call to POST /public/v1/posts on Postiz.
    Returns dict: {success, external_post_id, response_data, error_message}
    """
    try:
        api_key, timeout = _get_api_key_and_timeout()
        payload = _build_postiz_payload(post)

        headers = {
            # IMPORTANT: Postiz expects raw API key, not "Bearer x"
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        # Log request for debugging
        frappe.log_error(
            f"Postiz API Request:\nURL: {POSTIZ_POSTS_URL}\nPayload:\n{json.dumps(payload, indent=2)}",
            "Postiz API Request",
        )

        response = requests.post(
            POSTIZ_POSTS_URL,
            json=payload,
            headers=headers,
            timeout=timeout,
        )

        try:
            response_data = response.json()  # if response.text else {}
        except Exception:
            response_data = {"raw_response": response.text}

        if response.status_code in (200, 201):

            external_post_id = None

            # Postiz returns: [ { postId, integration } ]
            if isinstance(response_data, list) and len(response_data) > 0:
                external_post_id = response_data[0].get("postId")

            # Postiz also sometimes returns object:
            if isinstance(response_data, dict):
                external_post_id = response_data.get("postId") or response_data.get(
                    "data", {}
                ).get("id")

            return {
                "success": True,
                "external_post_id": external_post_id,
                "response_data": response_data,
            }

        error_message = (
            response_data.get("message")
            if isinstance(response_data, dict)
            else response.text
        )
        # Convert list/dict to string to prevent Frappe validation error
        if isinstance(error_message, (list, dict)):
            error_message = json.dumps(error_message, indent=2)

        return {
            "success": False,
            "error_message": error_message,
            "response_data": response_data,
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error_message": _("Postiz API request timed out."),
            "response_data": {},
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error_message": _(
                "Could not connect to Postiz API (check localhost:5000)."
            ),
            "response_data": {},
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error_message": f"Postiz API request failed: {str(e)}",
            "response_data": {},
        }
    except Exception as e:
        frappe.log_error(
            f"Unexpected error in Postiz API call: {frappe.get_traceback()}"
        )
        return {
            "success": False,
            "error_message": f"Unexpected error: {str(e)}",
            "response_data": {},
        }


@frappe.whitelist()
def get_post_status(post_id):
    """
    Simple helper to return local status from Frappe.
    (Does not call Postiz; use refresh_post_status_from_api for that.)
    """
    try:
        post = frappe.get_doc("Social Media Post", post_id)
        return {
            "success": True,
            "post_id": post_id,
            "status": post.status,
            "external_post_id": post.external_post_id,
            "error_message": post.error_message,
            "scheduled_at": post.scheduled_at,
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def cancel_scheduled_post(post_id):
    """
    Cancel a scheduled post in Postiz (and mark as Cancelled in ERPNext).
    Uses DELETE /public/v1/posts/:id
    """
    try:
        post = frappe.get_doc("Social Media Post", post_id)

        if post.status != "Scheduled":
            return {
                "success": False,
                "message": _("Only scheduled posts can be cancelled."),
            }

        if not post.external_post_id:
            # Allow local-only cancel if for some reason we don't have Postiz ID
            post.status = "Cancelled"
            post.error_message = _("Cancelled locally - no external Postiz post ID.")
            post.save(ignore_permissions=True)
            frappe.db.commit()
            return {
                "success": True,
                "message": _("Post marked as Cancelled locally (no Postiz ID)."),
            }

        api_key, timeout = _get_api_key_and_timeout()

        url = f"{POSTIZ_POSTS_URL}/{post.external_post_id}"
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        response = requests.delete(url, headers=headers, timeout=timeout)

        # Docs: DELETE /public/v1/posts/:id returns { "id": "..." }
        if response.status_code in (200, 204):
            post.status = "Cancelled"
            post.save(ignore_permissions=True)
            frappe.db.commit()
            return {
                "success": True,
                "message": _("Post cancelled successfully in Postiz."),
            }
        elif response.status_code == 404:
            # Not found in Postiz => still cancel locally
            post.status = "Cancelled"
            post.error_message = _("Post not found in Postiz; cancelled locally.")
            post.save(ignore_permissions=True)
            frappe.db.commit()
            return {
                "success": True,
                "message": _("Post not found in Postiz; cancelled locally."),
            }
        else:
            return {
                "success": False,
                "message": f"Failed to cancel in Postiz: {response.text}",
            }

    except Exception as e:
        frappe.log_error(f"Error cancelling post in Postiz: {frappe.get_traceback()}")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def refresh_post_status_from_api(post_id):
    """
    Fetch latest status from Postiz using the public 'Post list' endpoint:
    GET /public/v1/posts?startDate=...&endDate=...

    We search a small window around the scheduled time and match by ID.
    """
    try:
        post = frappe.get_doc("Social Media Post", post_id)

        if not post.external_post_id:
            return {"success": False, "message": _("No external Postiz post ID found.")}

        api_key, timeout = _get_api_key_and_timeout()

        # Choose a 1-day window around scheduled_time (or around now as fallback)
        base_dt = post.scheduled_time or frappe.utils.now_datetime()
        start = (base_dt - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        end = (base_dt + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        params = {"startDate": start, "endDate": end}

        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        response = requests.get(
            POSTIZ_POSTS_URL, headers=headers, params=params, timeout=timeout
        )

        data = response.json() if response.text else {}

        if response.status_code != 200:
            return {
                "success": False,
                "message": f"Failed to fetch status from Postiz: {response.text}",
            }

        # Docs: response = { "posts": [ { "id", "content", "publishDate", "state", "integration": {...} } ] }
        target = None
        for item in data.get("posts", []):
            if item.get("id") == post.external_post_id:
                target = item
                break

        if not target:
            return {
                "success": False,
                "message": _("Post not found in Postiz list for selected window."),
            }

        state = (target.get("state") or "").upper()

        if state == "QUEUE":
            post.status = "Scheduled"
        elif state == "PUBLISHED":
            post.status = "Published"
            post.published_at = target.get("publishDate")
        elif state == "ERROR":
            post.status = "Schedule Failed"
            post.error_message = _("Postiz status: ERROR")
        elif state == "DRAFT":
            post.status = "Draft"

        post.api_response = json.dumps(target, indent=2)
        post.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Status updated from Postiz."),
            "status": post.status,
            "data": target,
        }

    except Exception as e:
        frappe.log_error(f"Error refreshing Postiz status: {frappe.get_traceback()}")
        return {"success": False, "message": str(e)}
