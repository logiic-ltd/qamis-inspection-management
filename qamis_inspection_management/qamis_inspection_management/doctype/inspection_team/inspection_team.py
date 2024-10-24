# Copyright (c) 2023, Bailly Rurangirwa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

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
            try:
                inspection = frappe.get_doc("Inspection", self.inspection)
                inspection.update_team_counts()
                inspection.save()
            except frappe.DoesNotExistError:
                frappe.msgprint(f"Inspection {self.inspection} not found. It may have been deleted or not yet created.")
        # If inspection is not set, we don't need to do anything

@frappe.whitelist()
def create_inspection_team(team_name, members, schools, inspection=None):
    try:
        members = json.loads(members)
        schools = json.loads(schools)

        team_doc = frappe.get_doc({
            "doctype": "Inspection Team",
            "team_name": team_name,
            "inspection": inspection
        })

        for member in members:
            team_doc.append("members", {
                "id": member.get("id"),
                "username": member.get("username"),
                "displayName": member.get("displayName")
            })

        for school in schools:
            team_doc.append("schools", {
                "school_code": school.get("id"),
                "school_name": school.get("schoolName"),
                "province": school.get("province"),
                "district": school.get("district")
            })

        team_doc.insert(ignore_permissions=True)
        team_doc.save(ignore_permissions=True)

        return {
            "name": team_doc.name,
            "team_name": team_doc.team_name,
            "members_count": len(team_doc.members),
            "schools_count": len(team_doc.schools)
        }
    except Exception as e:
        frappe.log_error(f"Error creating Inspection Team: {str(e)}")
        return None
