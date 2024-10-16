import frappe
from frappe.model.document import Document
import json
import requests

class Inspection(Document):
    def before_save(self):
        self.fetch_external_data()

    def fetch_external_data(self):
        # Fetch data from external API and store as JSON strings
        self.checklists = json.dumps(self.get_checklists_from_external_service())
        self.schools = json.dumps(self.get_schools_from_external_service())

    def get_checklists_from_external_service(self):
        # TODO: Replace with actual API call to DHIS2
        return [{"id": "dataset1", "name": "Checklist A"}, {"id": "dataset2", "name": "Checklist B"}]

    def get_schools_from_external_service(self):
        # TODO: Replace with actual API call to DHIS2
        return [{"id": "ou1", "name": "School X"}, {"id": "ou2", "name": "School Y"}]

    def load_external_data(self):
        # Helper method to load JSON data into Python objects
        self.checklists_data = json.loads(self.checklists)
        self.schools_data = json.loads(self.schools)

@frappe.whitelist()
def search_users(search_term):
    url = f"http://localhost:8081/api/dhis2users/search/name?name={search_term}&page=0&size=20&sort=username,asc"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['content']
    else:
        frappe.throw("Error fetching users from external API")
