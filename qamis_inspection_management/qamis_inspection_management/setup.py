import frappe
import os

def setup_roles_and_workflow():
    roles = ["Division Manager", "Head of Department", "Director General"]
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role
            }).insert(ignore_permissions=True)
    workflow_file_path = os.path.join(os.path.dirname(__file__), 'workflow', 'inspection_workflow.json')
    workflow_data = frappe.get_file_json(workflow_file_path)
    if not frappe.db.exists('Workflow', {'workflow_name': workflow_data['workflow_name']}):
        workflow_doc = frappe.get_doc(workflow_data)
        workflow_doc.insert(ignore_permissions=True, ignore_links=True)
        
        # Insert workflow states explicitly
        for state in workflow_data['states']:
            if not frappe.db.exists('Workflow State', {'state': state['state']}):
                frappe.get_doc({
                    "doctype": "Workflow State",
                    "workflow_state_name": state['state'],  # Ensure the state name is set
                    "state": state['state'],
                    "doc_status": state['doc_status'],
                    "allow_edit": state['allow_edit']
                }).insert(ignore_permissions=True, ignore_links=True)

def remove_roles_and_workflow():
    roles = ["Division Manager", "Head of Department", "Director General"]
    for role in roles:
        if frappe.db.exists("Role", role):
            frappe.delete_doc("Role", role, ignore_permissions=True, ignore_linked_doctypes=True)
    if frappe.db.exists('Workflow', {'workflow_name': 'Inspection Workflow'}):
        workflow_doc = frappe.get_doc('Workflow', {'workflow_name': 'Inspection Workflow'})
        for state in workflow_doc.states:
            frappe.delete_doc('Workflow State', state.state, ignore_permissions=True)
        for action in workflow_doc.transitions:
            if frappe.db.exists('Workflow Action', action.action):
                frappe.delete_doc('Workflow Action', action.action, ignore_permissions=True, ignore_linked_doctypes=True)
        frappe.delete_doc('Workflow', 'Inspection Workflow', ignore_permissions=True)
