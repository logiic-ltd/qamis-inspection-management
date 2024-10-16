import frappe
from frappe.model.document import Document
import json

class Inspection(Document):
    def before_save(self):
        self.fetch_external_data()

    def fetch_external_data(self):
        # Fetch data from external API and store as JSON strings
        self.team_members = json.dumps(self.get_users_from_external_service())
        self.checklists = json.dumps(self.get_checklists_from_external_service())
        self.schools = json.dumps(self.get_schools_from_external_service())

    def get_users_from_external_service(self):
        # TODO: Replace with actual API call to DHIS2
        return [{"id": "user1", "name": "John Doe"}, {"id": "user2", "name": "Jane Smith"}]

    def get_checklists_from_external_service(self):
        # TODO: Replace with actual API call to DHIS2
        return [{"id": "dataset1", "name": "Checklist A"}, {"id": "dataset2", "name": "Checklist B"}]

    def get_schools_from_external_service(self):
        # TODO: Replace with actual API call to DHIS2
        return [{"id": "ou1", "name": "School X"}, {"id": "ou2", "name": "School Y"}]

    def load_external_data(self):
        # Helper method to load JSON data into Python objects
        self.team_members_data = json.loads(self.team_members)
        self.checklists_data = json.loads(self.checklists)
        self.schools_data = json.loads(self.schools)
