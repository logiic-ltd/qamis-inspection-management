import frappe
from frappe.model.document import Document
from frappe import _
import requests
import json
import logging
from qamis_inspection_management.config.api_config import API_BASE_URL

logger = logging.getLogger(__name__)

class Inspection(Document):
    def validate(self):
        self.validate_dates()
        self.validate_teams()
        self.validate_status_transition()

    def validate_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw(_("End Date cannot be before Start Date"))

    def validate_teams(self):
        if not self.inspection_teams:
            frappe.throw(_("At least one team must be added to the inspection."))

    def validate_status_transition(self):
        if not self.is_new():
            old_status = self.get_doc_before_save().status
            if old_status == "Draft" and self.status == "Approved":
                frappe.throw(_("Inspection cannot be directly approved from Draft status. Please set to Pending Review first."))
            elif old_status == "Approved" and self.status in ["Draft", "Pending Review"]:
                frappe.throw(_("Approved inspections cannot be set back to Draft or Pending Review status."))

    def on_update(self):
        self.update_team_links()

    def update_team_links(self):
        for team in self.inspection_teams:
            if frappe.db.exists("Inspection Team", team.team):
                team_doc = frappe.get_doc("Inspection Team", team.team)
                team_doc.parent = self.name
                team_doc.save(ignore_permissions=True)

@frappe.whitelist()
def search_users(search_term):
    url = f"{API_BASE_URL}/api/dhis2users/search/name?name={search_term}&page=0&size=20&sort=username,asc"
    return _make_api_request(url, "users")

@frappe.whitelist()
def search_checklists(search_term):
    url = f"{API_BASE_URL}/api/dhis2datasets/search/name?name={search_term}&page=0&size=20&sort=name,asc"
    return _make_api_request(url, "checklists")

@frappe.whitelist()
def search_schools(search_term):
    url = f"{API_BASE_URL}/api/schools/search?name={search_term}&page=0&size=20&sort=schoolName,asc"
    return _make_api_request(url, "schools")

def _make_api_request(url, item_type):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['content']
    except requests.exceptions.RequestException as e:
        logger.error(f"API Connection Error for {item_type}: {str(e)}")
        frappe.log_error(f"API Connection Error for {item_type}: {str(e)}")
        frappe.msgprint(_("Unable to fetch {0} from the external API. Please try again later.").format(item_type))
        return []
    except Exception as e:
        logger.error(f"Unexpected Error in _make_api_request for {item_type}: {str(e)}")
        frappe.log_error(f"Unexpected Error in _make_api_request for {item_type}: {str(e)}")
        frappe.msgprint(_("An unexpected error occurred while fetching {0}. Please try again later.").format(item_type))
        return []

@frappe.whitelist()
def create_inspection_team(team_name, members, schools, inspection=None):
    try:
        members_data = json.loads(members)
        schools_data = json.loads(schools)

        team_doc = frappe.get_doc({
            "doctype": "Inspection Team",
            "team_name": team_name,
            "members": [{"id": m["id"], "username": m["username"], "display_name": m["displayName"]} for m in members_data],
            "schools": [{"school_code": s["id"], "school_name": s["schoolName"], "province": s.get("province", ""), "district": s.get("district", "")} for s in schools_data]
        })
        
        if inspection:
            team_doc.parent = inspection

        team_doc.insert(ignore_permissions=True)
        
        return {
            "name": team_doc.name,
            "team_name": team_doc.team_name,
            "members_count": len(team_doc.members),
            "schools_count": len(team_doc.schools),
            "parent": team_doc.parent
        }
    except Exception as e:
        logger.error(f"Error creating Inspection Team: {str(e)}")
        frappe.log_error(f"Error creating Inspection Team: {str(e)}")
        frappe.throw(_("An error occurred while creating the inspection team. Please check the error log for details."))

def on_submit(doc, method):
    if doc.status == "Draft":
        doc.status = "Pending Review"
        doc.save()
    frappe.msgprint(_("Inspection submitted successfully and status updated to Pending Review"))
