frappe.ui.form.on('Inspection', {
    refresh: function(frm) {
        frm.add_custom_button(__('Manage Teams and Schools'), function() {
            show_team_management_dialog(frm);
        });
        frm.add_custom_button(__('Add Checklist'), function() {
            show_checklist_search_dialog(frm);
        });
        update_team_summary(frm);
    },
    before_save: function(frm) {
        if (frm.is_new()) {
            frm.doc.teams = frm.teams_data || [];
            frm.doc.school_assignments = frm.school_assignments_data || [];
        }
    }
});

function show_team_management_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: 'Manage Teams and Schools',
        width: 1200, // Set a wide width for the dialog
        fields: [
            {
                fieldname: 'team_name',
                fieldtype: 'Data',
                label: 'Team Name',
                reqd: 1
            },
            {
                fieldname: 'team_members_schools_section',
                fieldtype: 'Section Break',
                label: 'Team Members and Schools'
            },
            {
                fieldname: 'team_members_column',
                fieldtype: 'Column Break',
                label: 'Team Members'
            },
            {
                fieldname: 'member_search',
                fieldtype: 'Data',
                label: 'Search Team Members'
            },
            {
                fieldname: 'member_results',
                fieldtype: 'HTML'
            },
            {
                fieldname: 'selected_members',
                fieldtype: 'Table',
                label: 'Selected Members',
                fields: [
                    {
                        fieldname: 'id',
                        fieldtype: 'Data',
                        label: 'ID',
                        in_list_view: 1
                    },
                    {
                        fieldname: 'displayName',
                        fieldtype: 'Data',
                        label: 'Name',
                        in_list_view: 1
                    }
                ]
            },
            {
                fieldname: 'schools_column',
                fieldtype: 'Column Break',
                label: 'Schools'
            },
            {
                fieldname: 'school_search',
                fieldtype: 'Data',
                label: 'Search Schools'
            },
            {
                fieldname: 'school_results',
                fieldtype: 'HTML'
            },
            {
                fieldname: 'selected_schools',
                fieldtype: 'Table',
                label: 'Selected Schools',
                fields: [
                    {
                        fieldname: 'id',
                        fieldtype: 'Data',
                        label: 'ID',
                        in_list_view: 1
                    },
                    {
                        fieldname: 'schoolName',
                        fieldtype: 'Data',
                        label: 'School Name',
                        in_list_view: 1
                    }
                ]
            },
            {
                fieldname: 'teams_section',
                fieldtype: 'Section Break',
                label: 'Created Teams'
            },
            {
                fieldname: 'teams',
                fieldtype: 'Table',
                label: 'Teams',
                fields: [
                    {
                        fieldname: 'team_name',
                        fieldtype: 'Data',
                        in_list_view: 1,
                        label: 'Team Name'
                    },
                    {
                        fieldname: 'members',
                        fieldtype: 'Small Text',
                        label: 'Members'
                    },
                    {
                        fieldname: 'schools',
                        fieldtype: 'Small Text',
                        label: 'Schools'
                    }
                ]
            }
        ],
        primary_action_label: 'Save',
        primary_action(values) {
            save_teams_and_schools(frm, values.teams);
            d.hide();
            frm.save();
        }
    });

    // Initialize search functionality
    init_member_search(d);
    init_school_search(d);

    // Add team button
    d.add_custom_action('Add Team', () => {
        add_team_to_list(d);
    }, 'btn-primary');
    
    d.show();
}

function init_member_search(dialog) {
    let $search_input = dialog.fields_dict.member_search.$input;
    let $results = dialog.fields_dict.member_results.$wrapper;
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
                args: { search_term: search_term },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let results = r.message;
                        let html = results.map(item => `
                            <div class="member-item" style="cursor: pointer; padding: 5px; border-bottom: 1px solid #ccc;">
                                <strong>${frappe.utils.escape_html(item.displayName)}</strong>
                                <br>
                                <small>${frappe.utils.escape_html(item.username)}</small>
                            </div>
                        `).join('');
                        $results.html(html);

                        $results.find('.member-item').on('click', function() {
                            let index = $(this).index();
                            let item = results[index];
                            add_member_to_selection(dialog, item);
                        });
                    } else {
                        $results.html('<p>No results found</p>');
                    }
                }
            });
        }, 300);
    });
}

function init_school_search(dialog) {
    let $search_input = dialog.fields_dict.school_search.$input;
    let $results = dialog.fields_dict.school_results.$wrapper;
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
                method: 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_schools',
                args: { search_term: search_term },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let results = r.message;
                        let html = results.map(item => `
                            <div class="school-item" style="cursor: pointer; padding: 5px; border-bottom: 1px solid #ccc;">
                                <strong>${frappe.utils.escape_html(item.schoolName)}</strong>
                                <br>
                                <small>${frappe.utils.escape_html(item.province + ', ' + item.district)}</small>
                            </div>
                        `).join('');
                        $results.html(html);

                        $results.find('.school-item').on('click', function() {
                            let index = $(this).index();
                            let item = results[index];
                            add_school_to_selection(dialog, item);
                        });
                    } else {
                        $results.html('<p>No results found</p>');
                    }
                }
            });
        }, 300);
    });
}

function add_member_to_selection(dialog, member) {
    let selected_members = dialog.fields_dict.selected_members.get_value() || [];
    if (!selected_members.some(m => m.id === member.id)) {
        selected_members.push({
            id: member.id,
            displayName: member.displayName
        });
        dialog.set_value('selected_members', selected_members);
    }
}

function add_school_to_selection(dialog, school) {
    let selected_schools = dialog.fields_dict.selected_schools.get_value() || [];
    if (!selected_schools.some(s => s.id === school.id)) {
        selected_schools.push({
            id: school.id,
            schoolName: school.schoolName
        });
        dialog.set_value('selected_schools', selected_schools);
    }
}

function add_team_to_list(dialog) {
    let team_name = dialog.get_value('team_name');
    let selected_members = dialog.get_value('selected_members') || [];
    let selected_schools = dialog.get_value('selected_schools') || [];

    if (!team_name || selected_members.length === 0 || selected_schools.length === 0) {
        frappe.msgprint('Please enter a team name, select at least one member and one school.');
        return;
    }

    let teams = dialog.get_value('teams') || [];
    teams.push({
        team_name: team_name,
        members: selected_members.map(m => m.displayName).join(', '),
        schools: selected_schools.map(s => s.schoolName).join(', ')
    });

    dialog.set_value('teams', teams);
    dialog.set_value('team_name', '');
    dialog.set_value('selected_members', []);
    dialog.set_value('selected_schools', []);
}

function add_new_team(frm) {
    let d = new frappe.ui.Dialog({
        title: 'Add New Team',
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
            let new_team = {
                team_name: values.team_name,
                members: [],
                schools: []
            };
            frm.teams_data = frm.teams_data || [];
            frm.teams_data.push(new_team);
            d.hide();
            show_team_management_dialog(frm);
        }
    });
    d.show();
}

function remove_team(frm, teamIndex) {
    frm.teams_data.splice(teamIndex, 1);
    show_team_management_dialog(frm);
}

function show_user_search_dialog(frm, teamIndex) {
    show_search_dialog(frm, 'Team Member', 'users', 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_users', function(user) {
        add_team_member(frm, user, teamIndex);
    });
}

function add_team_member(dialog, user) {
    let teams = dialog.get_value('teams');
    if (teams && teams.length > 0) {
        let team = teams[0];  // Add to the first team for simplicity
        team.members = team.members || [];
        team.members.push({
            id: user.id,
            username: user.username,
            displayName: user.displayName
        });
        dialog.refresh_field('teams');
    } else {
        frappe.msgprint(__('Please add a team first.'));
    }
}

function add_school_to_team(dialog, school) {
    let teams = dialog.get_value('teams');
    if (teams && teams.length > 0) {
        let team = teams[0];  // Add to the first team for simplicity
        team.schools = team.schools || [];
        team.schools.push({
            id: school.id,
            school_code: school.schoolCode,
            school_name: school.schoolName
        });
        dialog.refresh_field('teams');
    } else {
        frappe.msgprint(__('Please add a team first.'));
    }
}

function save_teams_and_schools(frm, teams) {
    frm.doc.teams = teams;
    frm.doc.school_assignments = [];

    teams.forEach(team => {
        (team.schools || []).forEach(school => {
            frm.doc.school_assignments.push({
                team: team.team_name,
                school: school.school_code
            });
        });
    });

    frm.refresh_field('teams');
    frm.refresh_field('school_assignments');
    update_team_summary(frm);
}

function update_team_summary(frm) {
    if (!frm.teams_data) return;

    let summary = frm.teams_data.map(team => `
        <div class="team-summary">
            <h4>${team.team_name}</h4>
            <p>Members: ${team.members.length}, Schools: ${team.schools.length}</p>
        </div>
    `).join('');

    $(frm.fields_dict.teams_section.wrapper).find('.frappe-control[data-fieldname="teams"]').before(`
        <div class="team-summary-container">
            ${summary}
        </div>
    `);
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
        }, 500);
    });

    d.show();
}

function add_checklist(frm, checklist) {
    let new_checklist = {
        doctype: 'Inspection Checklist',
        id: checklist.id,
        name: checklist.name,
        short_name: checklist.shortName,
        period_type: checklist.periodType,
        last_updated: checklist.lastUpdated
    };
    frm.add_child('checklists', new_checklist);
    frm.refresh_field('checklists');
    frappe.show_alert(`Added ${checklist.name} (${checklist.shortName}) to the checklists`, 5);
}
