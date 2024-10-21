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
        fields: [
            {
                fieldname: 'search_section',
                fieldtype: 'Section Break',
                label: 'Search'
            },
            {
                fieldname: 'member_search',
                fieldtype: 'Data',
                label: 'Search Team Members',
                onchange: () => perform_search(d, 'member', frm)
            },
            {
                fieldname: 'col_break',
                fieldtype: 'Column Break'
            },
            {
                fieldname: 'school_search',
                fieldtype: 'Data',
                label: 'Search Schools',
                onchange: () => perform_search(d, 'school', frm)
            },
            {
                fieldname: 'results_section',
                fieldtype: 'Section Break',
                label: 'Search Results'
            },
            {
                fieldname: 'search_results',
                fieldtype: 'HTML'
            },
            {
                fieldname: 'teams_section',
                fieldtype: 'Section Break',
                label: 'Teams and Schools'
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
                        fieldtype: 'Table',
                        label: 'Members',
                        options: 'Inspection Team Member'
                    },
                    {
                        fieldname: 'schools',
                        fieldtype: 'Table',
                        label: 'Schools',
                        options: 'Team School Assignment'
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

    // Populate existing teams data
    d.set_value('teams', frm.doc.teams || []);
    d.show();
}

function perform_search(dialog, type, frm) {
    let search_term = dialog.get_value(type === 'member' ? 'member_search' : 'school_search');
    if (search_term.length < 2) {
        dialog.fields_dict.search_results.$wrapper.empty();
        return;
    }

    frappe.call({
        method: type === 'member' ? 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_users' : 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_schools',
        args: { search_term: search_term },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let results = r.message;
                let fields = results.map(item => ({
                    fieldtype: 'Button',
                    fieldname: `add_${item.id}`,
                    label: type === 'member' ? `Add ${item.displayName}` : `Add ${item.schoolName}`,
                    click: () => {
                        if (type === 'member') {
                            add_team_member(dialog, item);
                        } else {
                            add_school_to_team(dialog, item);
                        }
                    }
                }));
                
                dialog.fields_dict.search_results.df.fields = fields;
                dialog.fields_dict.search_results.refresh();
            } else {
                dialog.fields_dict.search_results.$wrapper.html('<p>No results found</p>');
            }
        }
    });
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
