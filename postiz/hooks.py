app_name = "postiz"
app_title = "Postiz"
app_publisher = "Abhishek"
app_description = "Post scheduler application"
app_email = "abhishekhiremath4949@gmail.com"
app_license = "mit"

# from . import api


# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "postiz",
# 		"logo": "/assets/postiz/logo.png",
# 		"title": "Postiz",
# 		"route": "/postiz",
# 		"has_permission": "postiz.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/postiz/css/postiz.css"
# app_include_js = "/assets/postiz/js/postiz.js"

# include js, css files in header of web template
# web_include_css = "/assets/postiz/css/postiz.css"
# web_include_js = "/assets/postiz/js/postiz.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "postiz/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "postiz/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "postiz.utils.jinja_methods",
# 	"filters": "postiz.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "postiz.install.before_install"
# after_install = "postiz.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "postiz.uninstall.before_uninstall"
# after_uninstall = "postiz.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "postiz.utils.before_app_install"
# after_app_install = "postiz.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "postiz.utils.before_app_uninstall"
# after_app_uninstall = "postiz.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "postiz.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"postiz.tasks.all"
# 	],
# 	"daily": [
# 		"postiz.tasks.daily"
# 	],
# 	"hourly": [
# 		"postiz.tasks.hourly"
# 	],
# 	"weekly": [
# 		"postiz.tasks.weekly"
# 	],
# 	"monthly": [
# 		"postiz.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "postiz.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "postiz.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "postiz.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["postiz.utils.before_request"]
# after_request = ["postiz.utils.after_request"]

# Job Events
# ----------
# before_job = ["postiz.utils.before_job"]
# after_job = ["postiz.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"postiz.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# override_whitelisted_methods = {
#     "postiz.postiz.api.fast_api.call_fastapi": "postiz.postiz.postiz.api.fast_api.call_fastapi"
# }

# doc_events = {
#     "Post Scheduler": {
#         "after_insert": "postiz.postiz.doctype.post_scheduler.post_scheduler.call_fastapi",
#         "on_update": "postiz.postiz.doctype.post_scheduler.post_scheduler.call_fastapi",
#     }
# }

# api_methods = {"postiz.api.webhooks.post_status_update": {"methods": ["POST"]}}

# doctype_js = {"Social Media Platform": "public/js/social_media_platform.js"}

# scheduler_events = {
#     "cron": {"* * * * *": ["postiz.postiz.api.post_scheduler.execute_scheduled_posts"]}
# }

# hooks.py
app_include_js = ["/assets/postiz/js/workspace.js"]  # We'll add JS here
scheduler_events = {"all": ["postiz.api.post_scheduler.publish_scheduled_posts"]}
