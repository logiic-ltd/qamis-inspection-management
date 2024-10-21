frappe.ui.form.on('Inspection', {
    refresh: function(frm) {
        frm.add_custom_button(__('Add Checklist'), function() {
            show_checklist_search_dialog(frm);
        });
        frm.add_custom_button(__('Add Team'), function() {
            show_team_dialog(frm);
        });
        frm.add_custom_button(__('Assign Schools'), function() {
            show_school_assignment_dialog(frm);
        });
    }
});

function show_checklist_search_dialog(frm) {
    show_search_dialog(frm, 'Checklist', 'checklists', 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_checklists', add_checklist);
}

function show_team_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: 'Add Team',
        fields: [
            {
                label: 'Team Name',
                fieldname: 'team_name',
                fieldtype: 'Data',
                reqd: 1
            }
        ],
        primary_action_label: 'Add',
        primary_action(values) {
            frappe.call({
                method: 'frappe.client.insert',
                args: {
                    doc: {
                        doctype: 'Inspection Team',
                        team_name: values.team_name,
                        inspection: frm.doc.name
                    }
                },
                callback: function(r) {
                    if (!r.exc) {
                        frm.reload_doc();
                        frappe.show_alert(`Team ${values.team_name} added`, 5);
                        show_user_search_dialog(frm, r.message.name);
                    }
                }
            });
            d.hide();
        }
    });
    d.show();
}

function show_user_search_dialog(frm, team_name) {
    show_search_dialog(frm, 'Team Member', 'users', 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_users', function(user) {
        add_team_member(frm, user, team_name);
    });
}

function show_school_assignment_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: 'Assign Schools to Teams',
        fields: [
            {
                label: 'Team',
                fieldname: 'team',
                fieldtype: 'Link',
                options: 'Inspection Team',
                get_query: function() {
                    return {
                        filters: {
                            'inspection': frm.doc.name
                        }
                    };
                },
                reqd: 1
            },
            {
                label: 'Schools',
                fieldname: 'schools_section',
                fieldtype: 'Section Break'
            },
            {
                fieldname: 'schools',
                fieldtype: 'Table',
                fields: [
                    {
                        label: 'School',
                        fieldname: 'school',
                        fieldtype: 'Link',
                        options: 'Inspection School',
                        in_list_view: 1,
                        reqd: 1
                    }
                ]
            }
        ],
        primary_action_label: 'Assign',
        primary_action(values) {
            values.schools.forEach(school => {
                frappe.call({
                    method: 'frappe.client.insert',
                    args: {
                        doc: {
                            doctype: 'Team School Assignment',
                            team: values.team,
                            school: school.school,
                            parent: frm.doc.name,
                            parenttype: 'Inspection',
                            parentfield: 'school_assignments'
                        }
                    }
                });
            });
            frm.reload_doc();
            frappe.show_alert(`Schools assigned to team ${values.team}`, 5);
            d.hide();
        }
    });
    d.show();
}

function show_search_dialog(frm, title, item_type, search_method, add_function) {
    let d = new frappe.ui.Dialog({
        title: `Search and Add ${title}`,
        fields: [
            {
                label: 'Search',
                fieldname: 'search_term',
                fieldtype: 'Data'
            },
            {
                label: 'Results',
                fieldname: 'results',
                fieldtype: 'HTML'
            }
        ],
        primary_action_label: 'Close',
        primary_action(values) {
            d.hide();
        }
    });

    let $results = d.fields_dict.results.$wrapper;
    let $search_input = d.fields_dict.search_term.$input;
    let searchTimeout;

    $search_input.on('input', function() {
        clearTimeout(searchTimeout);
        let search_term = $search_input.val();
        
        if (search_term.length < 2) {
            $results.empty();
            return;
        }

        $results.html('<p>Searching...</p>');

        searchTimeout = setTimeout(() => {
            frappe.call({
                method: search_method,
                args: {
                    search_term: search_term
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let items = r.message;
                        let html = items.map(item => `
                            <div class="${item_type}-item" style="cursor: pointer; padding: 5px; border-bottom: 1px solid #ccc;">
                                <strong>${frappe.utils.escape_html(item.name || item.displayName || item.schoolName)}</strong>
                                <br>
                                <small>${frappe.utils.escape_html(item.username || item.shortName || (item.province + ', ' + item.district))}</small>
                            </div>
                        `).join('');
                        $results.html(html);

                        $results.find(`.${item_type}-item`).on('click', function() {
                            let index = $(this).index();
                            let item = items[index];
                            add_function(item);
                            d.hide();
                        });
                    } else {
                        $results.html('<p>No results found or unable to connect to the API. Please try again later.</p>');
                    }
                }
            });
        }, 500); // Wait for 500ms after the user stops typing
    });

    d.show();
}

function add_team_member(frm, user, team_name) {
    frappe.call({
        method: 'frappe.client.insert',
        args: {
            doc: {
                doctype: 'Inspection Team Member',
                id: user.id,
                username: user.username,
                displayName: user.displayName,
                team: team_name
            }
        },
        callback: function(r) {
            if (!r.exc) {
                frm.reload_doc();
                frappe.show_alert(`Added ${user.displayName} to the team`, 5);
            }
        }
    });
}

function add_checklist(checklist) {
    frappe.call({
        method: 'frappe.client.insert',
        args: {
            doc: {
                doctype: 'Inspection Checklist',
                id: checklist.id,
                name: checklist.name,
                short_name: checklist.shortName,
                period_type: checklist.periodType,
                last_updated: checklist.lastUpdated,
                parent: cur_frm.doc.name,
                parenttype: 'Inspection',
                parentfield: 'checklists'
            }
        },
        callback: function(r) {
            if (!r.exc) {
                cur_frm.reload_doc();
                frappe.show_alert(`Added ${checklist.name} (${checklist.shortName}) to the checklists`, 5);
            }
        }
    });
}
