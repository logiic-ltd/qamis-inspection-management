from . import __version__ as app_version

app_name = "qamis_inspection_management"
app_title = "Qamis Inspection Management"
app_publisher = "Bailly Rurangirwa"
app_description = "Frappe-based application for managing the school inspection process, including scheduling, user assignment, checklist management, and multi-level approvals."
app_email = "rubailly@gmail.com"
app_license = "MIT"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "qamis_inspection_management",
# 		"logo": "/assets/qamis_inspection_management/logo.png",
# 		"title": "Qamis Inspection Management",
# 		"route": "/qamis_inspection_management",
# 		"has_permission": "qamis_inspection_management.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/qamis_inspection_management/css/qamis_inspection_management.css"
# app_include_js = "/assets/qamis_inspection_management/js/qamis_inspection_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/qamis_inspection_management/css/qamis_inspection_management.css"
# web_include_js = "/assets/qamis_inspection_management/js/qamis_inspection_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "qamis_inspection_management/public/scss/website"

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
# app_include_icons = "qamis_inspection_management/public/icons.svg"

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
# 	"methods": "qamis_inspection_management.utils.jinja_methods",
# 	"filters": "qamis_inspection_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "qamis_inspection_management.install.before_install"
# after_install = "qamis_inspection_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "qamis_inspection_management.uninstall.before_uninstall"
# after_uninstall = "qamis_inspection_management.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "qamis_inspection_management.utils.before_app_install"
# after_app_install = "qamis_inspection_management.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "qamis_inspection_management.utils.before_app_uninstall"
# after_app_uninstall = "qamis_inspection_management.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "qamis_inspection_management.notifications.get_notification_config"

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

override_doctype_class = {
	"Inspection": "qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.Inspection"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Inspection": {
		"on_update": "qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.Inspection.on_update",
		"on_cancel": "qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.on_cancel",
		"on_trash": "qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.on_trash"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"qamis_inspection_management.tasks.all"
# 	],
# 	"daily": [
# 		"qamis_inspection_management.tasks.daily"
# 	],
# 	"hourly": [
# 		"qamis_inspection_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"qamis_inspection_management.tasks.weekly"
# 	],
# 	"monthly": [
# 		"qamis_inspection_management.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "qamis_inspection_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "qamis_inspection_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "qamis_inspection_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["qamis_inspection_management.utils.before_request"]
# after_request = ["qamis_inspection_management.utils.after_request"]

# Job Events
# ----------
# before_job = ["qamis_inspection_management.utils.before_job"]
# after_job = ["qamis_inspection_management.utils.after_job"]

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
# 	"qamis_inspection_management.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

