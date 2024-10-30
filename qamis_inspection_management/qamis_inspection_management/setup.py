import frappe

def setup_workflow():
    workflow_data = frappe.get_file_json('qamis_inspection_management/qamis_inspection_management/workflow/inspection_workflow.json')
    if not frappe.db.exists('Workflow', {'workflow_name': workflow_data['workflow_name']}):
        workflow_doc = frappe.get_doc(workflow_data)
        workflow_doc.insert(ignore_permissions=True)

def remove_workflow():
    if frappe.db.exists('Workflow', {'workflow_name': 'Inspection Workflow'}):
        frappe.delete_doc('Workflow', 'Inspection Workflow', ignore_permissions=True)
