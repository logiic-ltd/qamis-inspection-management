import frappe
from frappe import _
from frappe.model.document import Document
import json
import requests
import logging
from qamis_inspection_management.config.api_config import API_BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def custom_save_method(self):
    logger.info("About to save document")
    logger.info(f"Document data: {self.as_dict()}")
    # Your existing save logic here
    super(Inspection, self).save()
    logger.info("Document saved successfully")

class Inspection(Document):
    def validate(self):
        logger.info(f"Validating Inspection: {self.name}")
        self.validate_dates()
        self.validate_status_transition()
        self.validate_teams()

    def save(self, *args, **kwargs):
        logger.info("About to save document")
        logger.info(f"Document data: {self.as_dict()}")
        super(Inspection, self).save(*args, **kwargs)
        logger.info("Document saved successfully")

    def validate_teams(self):
        if not self.teams:
            frappe.throw(_("At least one team must be added to the inspection."))
        for team in self.teams:
            if not team.team_name:
                frappe.throw(_("Team name is required for all teams."))
            if not team.get("members"):
                frappe.throw(_("Each team must have at least one member."))
            if not team.get("schools"):
                frappe.throw(_("Each team must have at least one school assigned."))

    def validate_status_transition(self):
        if not self.is_new():
            old_status = self.get_doc_before_save().status
            if old_status == "Draft" and self.status == "Approved":
                frappe.throw(_("Inspection cannot be directly approved from Draft status. Please set to Pending Review first."))
            elif old_status == "Approved" and self.status in ["Draft", "Pending Review"]:
                frappe.throw(_("Approved inspections cannot be set back to Draft or Pending Review status."))

    def before_save(self):
        logger.info(f"Before saving Inspection: {self.name}")
        self.update_count_fields()

    def update_count_fields(self):
        self.schools_count = 0
        self.team_members_count = 0
        for team in self.teams:
            team_doc = frappe.get_doc("Inspection Team", team.name)
            self.schools_count += team_doc.schools_count
            self.team_members_count += team_doc.members_count
        logger.info(f"Updated count fields for Inspection {self.name}: Schools: {self.schools_count}, Team Members: {self.team_members_count}")

    def on_update(self):
        logger.info(f"Updating Inspection: {self.name}")
        try:
            frappe.db.begin()
            self.update_or_create_teams()
            self.db_update()
            frappe.db.commit()
            logger.info(f"Inspection {self.name} updated successfully")
        except Exception as e:
            frappe.db.rollback()
            logger.error(f"Error updating Inspection {self.name}: {str(e)}")
            frappe.log_error(f"Error updating Inspection {self.name}: {str(e)}")
            frappe.throw(_("An error occurred while updating the inspection. Please check the error log for details."))

    def update_or_create_teams(self):
        try:
            # Iterate through each team in the Inspection
            for team in self.teams:
                team_data = {
                    "doctype": "Inspection Team",
                    "team_name": team.team_name,
                    "inspection": self.name
                }
                
                try:
                    # Check if the team already exists
                    existing_team = frappe.get_doc("Inspection Team", {"team_name": team.team_name})
                    # Update existing team
                    existing_team.update(team_data)
                    team_doc = existing_team
                except frappe.DoesNotExistError:
                    # Create new team
                    team_doc = frappe.get_doc(team_data)
                    team_doc.insert(ignore_permissions=True)
                
                # Ensure the team is linked to this inspection
                team_doc.inspection = self.name
                
                # Update team members
                team_doc.members = []
                for member in team.get("members", []):
                    team_doc.append("members", {
                        "id": member.get("id"),
                        "username": member.get("username"),
                        "displayName": member.get("displayName")
                    })
                
                # Update team schools
                team_doc.schools = []
                for school in team.get("schools", []):
                    team_doc.append("schools", {
                        "school_code": school.get("id"),
                        "school_name": school.get("schoolName")
                    })
                
                # Save the team document
                team_doc.save(ignore_permissions=True)
                logger.info(f"Team {team.team_name} saved successfully for Inspection {self.name}")
            
            # Update the inspection's team counts
            self.update_team_counts()
            self.db_update()
            frappe.db.commit()
            logger.info(f"Teams updated successfully for Inspection {self.name}")
        except Exception as e:
            logger.error(f"Error updating teams for Inspection {self.name}: {str(e)}")
            frappe.log_error(f"Error updating teams for Inspection {self.name}: {str(e)}")
            frappe.throw(_("An error occurred while updating the inspection teams. Please check the error log for details."))

    def update_team_counts(self):
        self.schools_count = 0
        self.team_members_count = 0
        for team in frappe.get_all("Inspection Team", filters={"inspection": self.name}, fields=["name"]):
            team_doc = frappe.get_doc("Inspection Team", team.name)
            self.schools_count += team_doc.schools_count
            self.team_members_count += team_doc.members_count

    def update_or_create_team_members(self, team_doc, members):
        existing_members = frappe.get_all("Inspection Team Member", 
            filters={"team": team_doc.name},
            fields=["name", "id"])
        
        existing_member_ids = {m.id: m.name for m in existing_members}
        
        for member in members:
            member_data = {
                "doctype": "Inspection Team Member",
                "team": team_doc.name,
                "id": member.get("id"),
                "username": member.get("username"),
                "displayName": member.get("displayName")
            }
            
            if member.get("id") in existing_member_ids:
                member_doc = frappe.get_doc("Inspection Team Member", existing_member_ids[member.get("id")])
                member_doc.update(member_data)
                member_doc.save(ignore_permissions=True)
            else:
                frappe.get_doc(member_data).insert(ignore_permissions=True)
        
        # Remove members that are no longer in the team
        for existing_id, existing_name in existing_member_ids.items():
            if existing_id not in [m.get("id") for m in members]:
                frappe.delete_doc("Inspection Team Member", existing_name, ignore_permissions=True)

    def update_or_create_team_schools(self, team_doc, schools):
        existing_schools = frappe.get_all("Team School Assignment", 
            filters={"team": team_doc.name},
            fields=["name", "school_code"])
        
        existing_school_codes = {s.school_code: s.name for s in existing_schools}
        
        for school in schools:
            school_data = {
                "doctype": "Team School Assignment",
                "team": team_doc.name,
                "school_code": school.get("id"),
                "school_name": school.get("schoolName")
            }
            
            if school.get("id") in existing_school_codes:
                school_doc = frappe.get_doc("Team School Assignment", existing_school_codes[school.get("id")])
                school_doc.update(school_data)
                school_doc.save(ignore_permissions=True)
            else:
                frappe.get_doc(school_data).insert(ignore_permissions=True)
        
        # Remove schools that are no longer assigned to the team
        for existing_code, existing_name in existing_school_codes.items():
            if existing_code not in [s.get("id") for s in schools]:
                frappe.delete_doc("Team School Assignment", existing_name, ignore_permissions=True)

    def after_insert(self):
        try:
            frappe.db.begin()
            self.update_or_create_teams()
            self.db_update()
            frappe.db.commit()
            logger.info(f"Inspection {self.name} inserted and teams created successfully")
        except Exception as e:
            frappe.db.rollback()
            logger.error(f"Error inserting Inspection {self.name}: {str(e)}")
            frappe.log_error(f"Error inserting Inspection {self.name}: {str(e)}")
            frappe.throw(_("An error occurred while creating the inspection. Please check the error log for details."))

    def validate_dates(self):
        logger.info(f"Validating dates for Inspection: {self.name}")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw(_("End Date cannot be before Start Date"))

@frappe.whitelist()
def search_users(search_term):
    logger.info(f"Searching users with term: {search_term}")
    try:
        url = f"{API_BASE_URL}/api/dhis2users/search/name?name={search_term}&page=0&size=20&sort=username,asc"
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
    url = f"{API_BASE_URL}/api/dhis2datasets/search/name?name={search_term}&page=0&size=20&sort=name,asc"
    return _make_api_request(url, "checklists")

@frappe.whitelist()
def search_schools(search_term):
    logger.info(f"Searching schools with term: {search_term}")
    url = f"{API_BASE_URL}/api/schools/search?name={search_term}&page=0&size=20&sort=schoolName,asc"
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

def on_submit(doc, method):
    logger.info(f"Inspection {doc.name} submitted")
    if doc.status == "Draft":
        doc.status = "Pending Review"
        doc.save()
    frappe.msgprint(_("Inspection submitted successfully and status updated to Pending Review"))
