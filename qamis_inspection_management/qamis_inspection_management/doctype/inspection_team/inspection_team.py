# Copyright (c) 2023, Bailly Rurangirwa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class InspectionTeam(Document):
    def validate(self):
        self.update_counts()

    def update_counts(self):
        self.members_count = len(self.members)
        self.schools_count = len(self.schools)

    def on_update(self):
        self.update_inspection()

    def update_inspection(self):
        if self.inspection:
            inspection = frappe.get_doc("Inspection", self.inspection)
            inspection.update_team_counts()
            inspection.save()
