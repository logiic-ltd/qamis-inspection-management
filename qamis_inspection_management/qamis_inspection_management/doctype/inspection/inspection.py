import frappe
from frappe.model.document import Document
import json
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Inspection(Document):
    pass

def before_save(doc, method):
    logger.info(f"Saving Inspection: {doc.name}")
    fetch_external_data(doc)

def fetch_external_data(doc):
    logger.info(f"Fetching external data for Inspection: {doc.name}")
    doc.checklists = json.dumps(get_checklists_from_external_service())
    doc.schools = json.dumps(get_schools_from_external_service())
    logger.info(f"External data fetched for Inspection: {doc.name}")

def get_checklists_from_external_service():
    logger.info("Fetching checklists from external service")
    # TODO: Replace with actual API call to DHIS2
    checklists = [{"id": "dataset1", "name": "Checklist A"}, {"id": "dataset2", "name": "Checklist B"}]
    logger.info(f"Fetched {len(checklists)} checklists")
    return checklists

def get_schools_from_external_service():
    logger.info("Fetching schools from external service")
    # TODO: Replace with actual API call to DHIS2
    schools = [{"id": "ou1", "name": "School X"}, {"id": "ou2", "name": "School Y"}]
    logger.info(f"Fetched {len(schools)} schools")
    return schools

@frappe.whitelist()
def search_users(search_term):
    logger.info(f"Searching users with term: {search_term}")
    url = f"http://192.168.0.100:8081/api/dhis2users/search/name?name={search_term}&page=0&size=20&sort=username,asc"
    try:
        logger.info(f"Sending request to: {url}")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Received {len(data['content'])} users from API")
            return data['content']
        else:
            logger.error(f"Error fetching users from API. Status code: {response.status_code}")
            frappe.msgprint("Error fetching users from external API. Please try again later.")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"API Connection Error: {str(e)}")
        frappe.msgprint("Unable to connect to the external API. Please check if the server is running and try again.")
        frappe.log_error(f"API Connection Error: {str(e)}")
        return []
