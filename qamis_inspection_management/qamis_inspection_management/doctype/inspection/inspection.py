import frappe
from frappe.model.document import Document
import json

class Inspection(Document):
    def before_save(self):
        self.fetch_external_data()

    def fetch_external_data(self):
        # Placeholder for external service calls
        # Replace these with actual API calls to your external service
        self.assigned_users = json.dumps(self.get_users_from_external_service())
        self.checklists = json.dumps(self.get_checklists_from_external_service())
        self.schools = json.dumps(self.get_schools_from_external_service())

    def get_users_from_external_service(self):
        # Placeholder method - replace with actual API call
        return [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}]

    def get_checklists_from_external_service(self):
        # Placeholder method - replace with actual API call
        return [{"id": 1, "name": "Checklist 1"}, {"id": 2, "name": "Checklist 2"}]

    def get_schools_from_external_service(self):
        # Placeholder method - replace with actual API call
        return [{"id": 1, "name": "School 1"}, {"id": 2, "name": "School 2"}]
