import frappe
from frappe import _
from frappe.model.document import Document
import json
import requests
import logging
from qamis_inspection_management.config.api_config import API_BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Inspection(Document):
    def validate(self):
        logger.info(f"Validating Inspection: {self.name}")
        self.validate_dates()
        self.validate_status_transition()

    def validate_status_transition(self):
        if not self.is_new():
            old_status = self.get_doc_before_save().status
            if old_status == "Draft" and self.status == "Approved":
                frappe.throw(_("Inspection cannot be directly approved from Draft status. Please set to Pending Review first."))
            elif old_status == "Approved" and self.status in ["Draft", "Pending Review"]:
                frappe.throw(_("Approved inspections cannot be set back to Draft or Pending Review status."))

    def before_save(self):
        logger.info(f"Before saving Inspection: {self.name}")
        self.update_count_fields()

    def update_count_fields(self):
        self.schools_count = 0
        self.team_members_count = 0
        for team in self.teams:
            team_doc = frappe.get_doc("Inspection Team", team.name)
            self.schools_count += team_doc.schools_count
            self.team_members_count += team_doc.members_count
        logger.info(f"Updated count fields for Inspection {self.name}: Schools: {self.schools_count}, Team Members: {self.team_members_count}")

    def on_update(self):
        logger.info(f"Updating Inspection: {self.name}")
        self.update_team_counts()
        logger.info(f"Inspection {self.name} updated")

    def update_team_counts(self):
        for team in self.teams:
            team_doc = frappe.get_doc("Inspection Team", team.name)
            team_doc.schools_count = len(team.schools)
            team_doc.members_count = len(team.members)
            team_doc.save()

    def on_update(self):
        logger.info(f"Updating Inspection: {self.name}")
        logger.info(f"Inspection {self.name} updated")

    def validate_dates(self):
        logger.info(f"Validating dates for Inspection: {self.name}")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw(_("End Date cannot be before Start Date"))

@frappe.whitelist()
def search_users(search_term):
    logger.info(f"Searching users with term: {search_term}")
    try:
        url = f"{API_BASE_URL}/api/dhis2users/search/name?name={search_term}&page=0&size=20&sort=username,asc"
        result = _make_api_request(url, "users")
        logger.info(f"Search users result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in search_users: {str(e)}")
        frappe.log_error(f"Error in search_users: {str(e)}")
        return []

@frappe.whitelist()
def search_checklists(search_term):
    logger.info(f"Searching checklists with term: {search_term}")
    url = f"{API_BASE_URL}/api/dhis2datasets/search/name?name={search_term}&page=0&size=20&sort=name,asc"
    return _make_api_request(url, "checklists")

@frappe.whitelist()
def search_schools(search_term):
    logger.info(f"Searching schools with term: {search_term}")
    url = f"{API_BASE_URL}/api/schools/search?name={search_term}&page=0&size=20&sort=schoolName,asc"
    return _make_api_request(url, "schools")

def _make_api_request(url, item_type):
    try:
        logger.info(f"Sending request to: {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
        data = response.json()
        logger.info(f"Received {len(data['content'])} {item_type} from API")
        return data['content']
    except requests.exceptions.RequestException as e:
        logger.error(f"API Connection Error for {item_type}: {str(e)}")
        frappe.log_error(f"API Connection Error for {item_type}: {str(e)}")
        frappe.msgprint(f"Unable to fetch {item_type} from the external API. Please try again later.")
        return []
    except ValueError as e:  # This will catch JSON decoding errors
        logger.error(f"JSON Decoding Error for {item_type}: {str(e)}")
        frappe.log_error(f"JSON Decoding Error for {item_type}: {str(e)}")
        frappe.msgprint(f"Error processing {item_type} data from the external API. Please try again later.")
        return []
    except Exception as e:
        logger.error(f"Unexpected Error in _make_api_request for {item_type}: {str(e)}")
        frappe.log_error(f"Unexpected Error in _make_api_request for {item_type}: {str(e)}")
        frappe.msgprint(f"An unexpected error occurred while fetching {item_type}. Please try again later.")
        return []

def on_submit(doc, method):
    logger.info(f"Inspection {doc.name} submitted")
    if doc.status == "Draft":
        doc.status = "Pending Review"
        doc.save()
    frappe.msgprint(_("Inspection submitted successfully and status updated to Pending Review"))
