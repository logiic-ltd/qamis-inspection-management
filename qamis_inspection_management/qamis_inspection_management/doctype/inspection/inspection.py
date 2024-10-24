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


class Inspection(Document):
    def validate(self):
        logger.info(f"Validating Inspection: {self.name}")
        self.validate_dates()
        self.validate_status_transition()
        self.validate_teams()

    def before_save(self):
        logger.info("About to save document")
        logger.info(f"Document data: {self.as_dict()}")

    def after_save(self):
        logger.info("Document saved successfully")

    def validate_teams(self):
        if not self.teams:
            frappe.throw(_("At least one team must be added to the inspection."))
        for team_link in self.teams:
            if not team_link.team_id:
                frappe.throw(_("Team ID is required for all teams."))
            try:
                team_doc = frappe.get_doc("Inspection Team", team_link.team_id)
                if not team_doc.members:
                    frappe.throw(_("Team {0} must have at least one member.").format(team_doc.team_name))
                if not team_doc.schools:
                    frappe.throw(_("Team {0} must have at least one school assigned.").format(team_doc.team_name))
            except frappe.DoesNotExistError:
                frappe.throw(_("Inspection Team {0} not found.").format(team_link.team_id))

    def validate_status_transition(self):
        if not self.is_new():
            old_status = self.get_doc_before_save().status
            if old_status == "Draft" and self.status == "Approved":
                frappe.throw(_("Inspection cannot be directly approved from Draft status. Please set to Pending Review first."))
            elif old_status == "Approved" and self.status in ["Draft", "Pending Review"]:
                frappe.throw(_("Approved inspections cannot be set back to Draft or Pending Review status."))

    def on_update(self):
        logger.info(f"Updating Inspection: {self.name}")
        logger.info(f"Teams before update: {[{'team': team.team_name} for team in self.teams]}")
        try:
            frappe.db.begin()
            self.link_teams()
            frappe.db.commit()
            logger.info(f"Inspection {self.name} updated successfully")
            logger.info(f"Teams after update: {[{'team': team.team_name} for team in self.teams]}")
        except Exception as e:
            frappe.db.rollback()
            logger.error(f"Error updating Inspection {self.name}: {str(e)}")
            frappe.log_error(f"Error updating Inspection {self.name}: {str(e)}")
            frappe.throw(_("An error occurred while updating the inspection. Please check the error log for details."))

    def link_teams(self):
        try:
            logger.info(f"Linking teams for Inspection {self.name}")
            
            # Get existing teams linked to this inspection
            existing_teams = frappe.get_all("Inspection Team", 
                filters={"inspection": self.name},
                fields=["name", "team_name"])
            existing_team_ids = {team.name: team.team_name for team in existing_teams}
            
            # Iterate through each team in the Inspection
            for team_link in self.get("teams", []):
                logger.info(f"Processing team: {team_link.team_id}")
                
                if team_link.team_id in existing_team_ids:
                    logger.info(f"Team {team_link.team_id} already linked to this inspection. Skipping.")
                    existing_team_ids.pop(team_link.team_id, None)
                    continue
                
                try:
                    team_doc = frappe.get_doc("Inspection Team", team_link.team_id)
                    if team_doc.inspection != self.name:
                        logger.info(f"Linking team {team_doc.name} to inspection {self.name}")
                        team_doc.inspection = self.name
                        team_doc.save(ignore_permissions=True)
                except frappe.DoesNotExistError:
                    logger.error(f"Inspection Team {team_link.team_id} not found.")
                    continue
            
            # Remove teams that are no longer in the inspection
            for team_id in existing_team_ids:
                team_doc = frappe.get_doc("Inspection Team", team_id)
                team_doc.inspection = None
                team_doc.save(ignore_permissions=True)
                logger.info(f"Removed team link: {team_id}")

            logger.info(f"Teams linked successfully for Inspection {self.name}")
        except Exception as e:
            logger.error(f"Error linking teams for Inspection {self.name}: {str(e)}")
            frappe.log_error(f"Error linking teams for Inspection {self.name}: {str(e)}")
            frappe.throw(_("An error occurred while linking the inspection teams. Please check the error log for details."))

    def update_or_create_team_members(self, team_doc, members):
        existing_members = frappe.get_all("Inspection Team Member", 
            filters={"team": team_doc.name},
            fields=["name", "id", "username", "displayName"])
        
        existing_member_ids = {m.id: m for m in existing_members}
        
        for member in members:
            member_data = {
                "doctype": "Inspection Team Member",
                "team": team_doc.name,
                "id": member.get("id"),
                "username": member.get("username"),
                "displayName": member.get("displayName")
            }
            
            if member.get("id") in existing_member_ids:
                existing_member = existing_member_ids[member.get("id")]
                if (existing_member.username != member.get("username") or 
                    existing_member.displayName != member.get("displayName")):
                    member_doc = frappe.get_doc("Inspection Team Member", existing_member.name)
                    member_doc.update(member_data)
                    member_doc.save(ignore_permissions=True)
                    logger.info(f"Updated member: {member.get('id')}")
            else:
                frappe.get_doc(member_data).insert(ignore_permissions=True)
                logger.info(f"Inserted new member: {member.get('id')}")
        
        # Remove members that are no longer in the team
        current_member_ids = [m.get("id") for m in members]
        for existing_id, existing_member in existing_member_ids.items():
            if existing_id not in current_member_ids:
                frappe.delete_doc("Inspection Team Member", existing_member.name, ignore_permissions=True)
                logger.info(f"Removed member: {existing_id}")

    def update_or_create_team_schools(self, team_doc, schools):
        existing_schools = {school.school_code: school for school in team_doc.schools}
        
        for school in schools:
            school_code = school.get("id")
            if school_code in existing_schools:
                existing_school = existing_schools[school_code]
                existing_school.school_name = school.get("schoolName")
                existing_school.province = school.get("province")
                existing_school.district = school.get("district")
            else:
                team_doc.append("schools", {
                    "school_code": school_code,
                    "school_name": school.get("schoolName"),
                    "province": school.get("province"),
                    "district": school.get("district")
                })
        
        # Remove schools that are no longer in the team
        team_doc.schools = [school for school in team_doc.schools if school.school_code in [s.get("id") for s in schools]]

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

@frappe.whitelist()
def create_inspection_team(team_name, members, schools):
    logger.info(f"Creating inspection team: {team_name}")
    logger.info(f"Members: {members}")
    logger.info(f"Schools: {schools}")
    try:
        team_doc = frappe.get_doc({
            "doctype": "Inspection Team",
            "team_name": team_name
        })

        for member in json.loads(members):
            logger.info(f"Adding member to team: {member}")
            team_doc.append("members", {
                "id": member.get("id"),
                "username": member.get("username"),
                "displayName": member.get("displayName")
            })

        for school in json.loads(schools):
            logger.info(f"Adding school to team: {school}")
            team_doc.append("schools", {
                "school_code": school.get("id"),
                "school_name": school.get("schoolName"),
                "province": school.get("province"),
                "district": school.get("district")
            })

        logger.info("Inserting team document")
        team_doc.insert(ignore_permissions=True)
        logger.info("Saving team document")
        team_doc.save(ignore_permissions=True)

        result = {
            "name": team_doc.name,
            "team_name": team_doc.team_name,
            "members_count": len(team_doc.members),
            "schools_count": len(team_doc.schools)
        }
        logger.info(f"Team created successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Error creating Inspection Team: {str(e)}")
        frappe.log_error(f"Error creating Inspection Team: {str(e)}")
        frappe.throw(_("An error occurred while creating the inspection team. Please check the error log for details."))

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
    def update_team_members_and_schools(self, team_doc, team_data):
        # Update team members
        team_doc.members = []
        for member in team_data.get("members", []):
            logger.info(f"Adding member to team: {member.get('displayName')}")
            team_doc.append("members", {
                "id": member.get("id"),
                "username": member.get("username"),
                "displayName": member.get("displayName")
            })

        # Update team schools
        team_doc.schools = []
        for school in team_data.get("schools", []):
            logger.info(f"Adding school to team: {school.get('schoolName')}")
            team_doc.append("schools", {
                "school_code": school.get("id"),
                "school_name": school.get("schoolName"),
                "province": school.get("province"),
                "district": school.get("district")
            })
