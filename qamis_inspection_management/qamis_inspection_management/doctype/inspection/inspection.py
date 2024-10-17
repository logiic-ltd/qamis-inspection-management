import frappe
from frappe.model.document import Document
import json
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Inspection(Document):
    def before_save(self):
        logger.info(f"Saving Inspection: {self.name}")
        self.fetch_external_data()

    def fetch_external_data(self):
        logger.info(f"Fetching external data for Inspection: {self.name}")
        self.checklists = json.dumps(self.get_checklists_from_external_service())
        self.schools = json.dumps(self.get_schools_from_external_service())
        logger.info(f"External data fetched for Inspection: {self.name}")

    def validate(self):
        self.validate_team_members()

    def validate_team_members(self):
        logger.info(f"Validating team members for Inspection: {self.name}")
        for member in self.team_members:
            if not all([member.id, member.username, member.displayName]):
                frappe.throw(_("All team member fields (ID, Username, Display Name) are required."))

    def get_checklists_from_external_service(self):
        logger.info("Fetching checklists from external service")
        # TODO: Replace with actual API call to DHIS2
        checklists = [{"id": "dataset1", "name": "Checklist A"}, {"id": "dataset2", "name": "Checklist B"}]
        logger.info(f"Fetched {len(checklists)} checklists")
        return checklists

    def get_schools_from_external_service(self):
        logger.info("Fetching schools from external service")
        # TODO: Replace with actual API call to DHIS2
        schools = [{"id": "ou1", "name": "School X"}, {"id": "ou2", "name": "School Y"}]
        logger.info(f"Fetched {len(schools)} schools")
        return schools

@frappe.whitelist()
def search_users(search_term):
    logger.info(f"Searching users with term: {search_term}")
    try:
        url = f"http://192.168.8.107:8081/api/dhis2users/search/name?name={search_term}&page=0&size=20&sort=username,asc"
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
    url = f"http://192.168.8.107:8081/api/dhis2datasets/search/name?name={search_term}&page=0&size=20&sort=name,asc"
    return _make_api_request(url, "checklists")

@frappe.whitelist()
def search_schools(search_term):
    logger.info(f"Searching schools with term: {search_term}")
    url = f"http://192.168.8.107:8081/api/schools/search?name={search_term}&page=0&size=20&sort=schoolName,asc"
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
