# Copyright (c) 2023, Bailly Rurangirwa and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import json

class InspectionChecklist(Document):
    def before_save(self):
        if isinstance(self.organization_units, list):
            self.organization_units = json.dumps(self.organization_units)

    def after_load(self):
        if self.organization_units:
            try:
                self.organization_units = json.loads(self.organization_units)
            except json.JSONDecodeError:
                pass  # If it's not valid JSON, leave it as is
