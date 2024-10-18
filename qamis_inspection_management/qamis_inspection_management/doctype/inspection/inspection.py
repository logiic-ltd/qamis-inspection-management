import frappe
from frappe import _
from frappe.model.document import Document
import json
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Inspection(Document):
    def validate(self):
        logger.info(f"Validating Inspection: {self.name}")
        self.fetch_external_data()
        self.validate_team_members()
        self.validate_dates()

    def fetch_external_data(self):
        logger.info(f"Fetching external data for Inspection: {self.name}")
        checklists = self.get_checklists_from_external_service()
        schools = self.get_schools_from_external_service()
        
        # Clear existing checklists and schools
        self.checklists = []
        self.schools = []
        
        # Add new checklists
        for checklist in checklists:
            checklist_doc = frappe.get_doc({
                "doctype": "Inspection Checklist",
                "id": checklist.get("id"),
                "name": checklist.get("name"),
                "short_name": checklist.get("shortName"),
                "period_type": checklist.get("periodType"),
                "last_updated": checklist.get("lastUpdated")
            })
            checklist_doc.insert(ignore_permissions=True)
            self.append("checklists", {"inspection_checklist": checklist_doc.name})
        
        # Add new schools
        for school in schools:
            self.append("schools", {
                "school_code": school.get("schoolCode"),
                "school_name": school.get("schoolName"),
                "province": school.get("province"),
                "district": school.get("district"),
                "sector": school.get("sector"),
                "cell": school.get("cell"),
                "village": school.get("village")
            })
        
        logger.info(f"External data fetched for Inspection: {self.name}")

    def on_update(self):
        logger.info(f"Updating Inspection: {self.name}")
        for checklist in self.checklists:
            if frappe.db.exists("Inspection Checklist", checklist.inspection_checklist):
                doc = frappe.get_doc("Inspection Checklist", checklist.inspection_checklist)
                doc.inspection = self.name
                doc.save(ignore_permissions=True)
        logger.info(f"Inspection {self.name} updated")

    def validate_team_members(self):
        logger.info(f"Validating team members for Inspection: {self.name}")
        for member in self.team_members:
            if not all([member.id, member.username, member.displayName]):
                frappe.throw(_("All team member fields (ID, Username, Display Name) are required."))

    def validate_dates(self):
        logger.info(f"Validating dates for Inspection: {self.name}")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw(_("End Date cannot be before Start Date"))

    def get_checklists_from_external_service(self):
        logger.info("Fetching checklists from external service")
        # TODO: Replace with actual API call to DHIS2
        checklists = [
            {
                "id": "dataset1",
                "name": "Checklist A",
                "shortName": "CA",
                "periodType": "Monthly",
                "lastUpdated": "2023-05-15 10:00:00"
            },
            {
                "id": "dataset2",
                "name": "Checklist B",
                "shortName": "CB",
                "periodType": "Quarterly",
                "lastUpdated": "2023-05-14 14:30:00"
            }
        ]
        logger.info(f"Fetched {len(checklists)} checklists")
        return checklists

    def get_schools_from_external_service(self):
        logger.info("Fetching schools from external service")
        # TODO: Replace with actual API call to DHIS2
        schools = [
            {
                "schoolCode": "SCH001",
                "schoolName": "School X",
                "province": "Province A",
                "district": "District 1",
                "sector": "Sector X",
                "cell": "Cell 1",
                "village": "Village A"
            },
            {
                "schoolCode": "SCH002",
                "schoolName": "School Y",
                "province": "Province B",
                "district": "District 2",
                "sector": "Sector Y",
                "cell": "Cell 2",
                "village": "Village B"
            }
        ]
        logger.info(f"Fetched {len(schools)} schools")
        return schools

@frappe.whitelist()
def search_users(search_term):
    logger.info(f"Searching users with term: {search_term}")
    try:
        url = f"http://192.168.0.101:8081/api/dhis2users/search/name?name={search_term}&page=0&size=20&sort=username,asc"
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
    url = f"http://192.168.0.101:8081/api/dhis2datasets/search/name?name={search_term}&page=0&size=20&sort=name,asc"
    return _make_api_request(url, "checklists")

@frappe.whitelist()
def search_schools(search_term):
    logger.info(f"Searching schools with term: {search_term}")
    url = f"http://192.168.0.101:8081/api/schools/search?name={search_term}&page=0&size=20&sort=schoolName,asc"
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
    # Add any logic you want to execute when the inspection is submitted
    frappe.msgprint(_("Inspection submitted successfully"))
