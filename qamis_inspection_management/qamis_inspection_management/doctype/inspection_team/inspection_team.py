from frappe.model.document import Document
import frappe
from frappe import _

class InspectionTeam(Document):
    def validate(self):
        self.validate_members()
        self.validate_schools()

    def validate_members(self):
        if not self.members:
            frappe.throw(_("At least one member must be added to the team."))

    def validate_schools(self):
        if not self.schools:
            frappe.throw(_("At least one school must be assigned to the team."))

    def on_update(self):
        self.update_inspection_link()

    def update_inspection_link(self):
        if self.parent:
            inspection = frappe.get_doc("Inspection", self.parent)
            team_exists = False
            for team in inspection.inspection_teams:
                if team.team == self.name:
                    team_exists = True
                    break
            if not team_exists:
                inspection.append("inspection_teams", {
                    "team": self.name,
                    "team_name": self.team_name
                })
                inspection.save(ignore_permissions=True, ignore_links=True)
