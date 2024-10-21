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
                fieldname: 'teams_html',
                fieldtype: 'HTML'
            }
        ],
        primary_action_label: 'Save',
        primary_action(values) {
            save_teams_and_schools(frm);
            d.hide();
            frm.save();
        }
    });

    d.fields_dict.teams_html.$wrapper.html(get_teams_html(frm));
    d.show();
}

function get_teams_html(frm) {
    let teams_data = frm.teams_data || [];
    let html = `
        <div id="teams-container">
            ${teams_data.map((team, index) => `
                <div class="team-section" data-team-index="${index}">
                    <h3>${team.team_name} <button class="btn btn-xs btn-default remove-team">Remove Team</button></h3>
                    <div class="team-members">
                        <h4>Team Members</h4>
                        ${(team.members || []).map(member => `
                            <div class="team-member">
                                ${member.displayName} (${member.username})
                                <button class="btn btn-xs btn-default remove-member" data-member-id="${member.id}">Remove</button>
                            </div>
                        `).join('')}
                        <button class="btn btn-xs btn-primary add-member">Add Member</button>
                    </div>
                    <div class="team-schools">
                        <h4>Assigned Schools</h4>
                        ${(team.schools || []).map(school => `
                            <div class="team-school">
                                ${school.school_name} (${school.school_code})
                                <button class="btn btn-xs btn-default remove-school" data-school-id="${school.id}">Remove</button>
                            </div>
                        `).join('')}
                        <button class="btn btn-xs btn-primary add-school">Add School</button>
                    </div>
                </div>
            `).join('')}
        </div>
        <button id="add-team" class="btn btn-sm btn-primary">Add New Team</button>
    `;

    setTimeout(() => {
        $('#add-team').on('click', () => add_new_team(frm));
        $('.remove-team').on('click', function() {
            let teamIndex = $(this).closest('.team-section').data('team-index');
            remove_team(frm, teamIndex);
        });
        $('.add-member').on('click', function() {
            let teamIndex = $(this).closest('.team-section').data('team-index');
            show_user_search_dialog(frm, teamIndex);
        });
        $('.remove-member').on('click', function() {
            let teamIndex = $(this).closest('.team-section').data('team-index');
            let memberId = $(this).data('member-id');
            remove_team_member(frm, teamIndex, memberId);
        });
        $('.add-school').on('click', function() {
            let teamIndex = $(this).closest('.team-section').data('team-index');
            show_school_search_dialog(frm, teamIndex);
        });
        $('.remove-school').on('click', function() {
            let teamIndex = $(this).closest('.team-section').data('team-index');
            let schoolId = $(this).data('school-id');
            remove_school(frm, teamIndex, schoolId);
        });
    }, 0);

    return html;
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

function add_team_member(frm, user, teamIndex) {
    let team_member = {
        id: user.id,
        username: user.username,
        displayName: user.displayName
    };
    
    frm.teams_data[teamIndex].members = frm.teams_data[teamIndex].members || [];
    frm.teams_data[teamIndex].members.push(team_member);
    show_team_management_dialog(frm);
}

function remove_team_member(frm, teamIndex, memberId) {
    frm.teams_data[teamIndex].members = frm.teams_data[teamIndex].members.filter(member => member.id !== memberId);
    show_team_management_dialog(frm);
}

function show_school_search_dialog(frm, teamIndex) {
    show_search_dialog(frm, 'School', 'schools', 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_schools', function(school) {
        add_school_to_team(frm, school, teamIndex);
    });
}

function add_school_to_team(frm, school, teamIndex) {
    let school_assignment = {
        id: school.id,
        school_code: school.schoolCode,
        school_name: school.schoolName
    };
    
    frm.teams_data[teamIndex].schools = frm.teams_data[teamIndex].schools || [];
    frm.teams_data[teamIndex].schools.push(school_assignment);
    show_team_management_dialog(frm);
}

function remove_school(frm, teamIndex, schoolId) {
    frm.teams_data[teamIndex].schools = frm.teams_data[teamIndex].schools.filter(school => school.id !== schoolId);
    show_team_management_dialog(frm);
}

function save_teams_and_schools(frm) {
    frm.teams_data = frm.teams_data || [];
    frm.school_assignments_data = [];

    frm.teams_data.forEach(team => {
        team.schools.forEach(school => {
            frm.school_assignments_data.push({
                doctype: 'Team School Assignment',
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
