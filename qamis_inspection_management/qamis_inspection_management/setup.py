import frappe

def setup_roles_and_workflow():
    roles = ["Division Manager", "Head of Department", "Director General"]
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role
            }).insert(ignore_permissions=True)
    workflow_data = frappe.get_file_json('qamis_inspection_management/qamis_inspection_management/workflow/inspection_workflow.json')
    if not frappe.db.exists('Workflow', {'workflow_name': workflow_data['workflow_name']}):
        workflow_doc = frappe.get_doc(workflow_data)
        workflow_doc.insert(ignore_permissions=True)

def remove_roles_and_workflow():
    roles = ["Division Manager", "Head of Department", "Director General"]
    for role in roles:
        if frappe.db.exists("Role", role):
            frappe.delete_doc("Role", role, ignore_permissions=True)
    if frappe.db.exists('Workflow', {'workflow_name': 'Inspection Workflow'}):
        frappe.delete_doc('Workflow', 'Inspection Workflow', ignore_permissions=True)
