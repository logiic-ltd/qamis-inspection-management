frappe.ui.form.on('Inspection', {
    refresh: function(frm) {
        frm.add_custom_button(__('Add Team Member'), function() {
            show_user_search_dialog(frm);
        });
        frm.add_custom_button(__('Add Checklist'), function() {
            show_checklist_search_dialog(frm);
        });
        frm.add_custom_button(__('Add School'), function() {
            show_school_search_dialog(frm);
        });
    }
});

function show_school_search_dialog(frm) {
    show_search_dialog(frm, 'School', 'schools', 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_schools', add_school);
}

function show_user_search_dialog(frm) {
    show_search_dialog(frm, 'Team Member', 'users', 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_users', add_team_member);
}

function show_checklist_search_dialog(frm) {
    show_search_dialog(frm, 'Checklist', 'checklists', 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_checklists', add_checklist);
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
                            add_function(frm, item);
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

function add_school(frm, school) {
    frm.add_child('schools', {
        school_code: school.schoolCode,
        school_name: school.schoolName,
        province: school.province,
        district: school.district,
        sector: school.sector,
        cell: school.cell,
        village: school.village
    });
    frm.refresh_field('schools');
    frm.save();
    frappe.show_alert(`Added ${school.schoolName} to the schools`, 5);
}

function show_user_search_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: 'Search and Add Team Member',
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
                method: 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_users',
                args: {
                    search_term: search_term
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let users = r.message;
                        let html = users.map(user => `
                            <div class="user-item" style="cursor: pointer; padding: 5px; border-bottom: 1px solid #ccc;">
                                <strong>${frappe.utils.escape_html(user.displayName)}</strong>
                                <br>
                                <small>${frappe.utils.escape_html(user.username)}</small>
                            </div>
                        `).join('');
                        $results.html(html);

                        $results.find('.user-item').on('click', function() {
                            let index = $(this).index();
                            let user = users[index];
                            add_team_member(frm, user);
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

function add_team_member(frm, user) {
    frm.add_child('team_members', {
        id: user.id,
        username: user.username,
        displayName: user.displayName
    });
    frm.refresh_field('team_members');
    frm.save()
        .then(() => {
            frappe.show_alert(`Added ${user.displayName} to the team`, 5);
        })
        .catch((err) => {
            console.error("Error saving team member:", err);
            frappe.msgprint(__("Error adding team member. Please try again."));
        });
}

function show_checklist_search_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: 'Search and Add Checklist',
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
                method: 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_checklists',
                args: {
                    search_term: search_term
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let checklists = r.message;
                        let html = checklists.map(checklist => `
                            <div class="checklist-item" style="cursor: pointer; padding: 5px; border-bottom: 1px solid #ccc;">
                                <strong>${frappe.utils.escape_html(checklist.name)}</strong>
                                <br>
                                <small>${frappe.utils.escape_html(checklist.id)}</small>
                            </div>
                        `).join('');
                        $results.html(html);

                        $results.find('.checklist-item').on('click', function() {
                            let index = $(this).index();
                            let checklist = checklists[index];
                            add_checklist(frm, checklist);
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

function add_checklist(frm, checklist) {
    frm.add_child('checklists', {
        id: checklist.id,
        name: checklist.name,
        short_name: checklist.shortName,
        period_type: checklist.periodType,
        last_updated: checklist.lastUpdated
    });
    frm.refresh_field('checklists');
    frm.save();
    frappe.show_alert(`Added ${checklist.name} (${checklist.shortName}) to the checklists`, 5);
}
