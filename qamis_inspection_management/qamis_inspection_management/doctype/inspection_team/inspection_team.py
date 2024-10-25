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
        if self.parent_inspection:
            self.update_inspection()

    def update_inspection(self):
        if self.parent:
            inspection = frappe.get_doc("Inspection", self.parent)
            for team in inspection.inspection_teams:
                if team.name == self.name:
                    team.team_name = self.team_name
                    team.members = self.members
                    team.schools = self.schools
                    team.members_count = self.members_count
                    team.schools_count = self.schools_count
            inspection.save(ignore_permissions=True)

@frappe.whitelist()
def create_inspection_team(team_name, members, schools, inspection=None):
    try:
        members = json.loads(members)
        schools = json.loads(schools)

        team_doc = frappe.get_doc({
            "doctype": "Inspection Team",
            "team_name": team_name
        })
        
        if inspection:
            # Check if the Inspection document exists
            if frappe.db.exists("Inspection", inspection):
                team_doc.inspection = inspection
            else:
                frappe.msgprint(f"Inspection {inspection} not found. Creating team without linking to inspection.")

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

        return {
            "name": team_doc.name,
            "team_name": team_doc.team_name,
            "members_count": len(team_doc.members),
            "schools_count": len(team_doc.schools),
            "inspection": team_doc.inspection
        }
    except Exception as e:
        frappe.log_error(f"Error creating Inspection Team: {str(e)}")
        frappe.throw(f"Error creating Inspection Team: {str(e)}")
