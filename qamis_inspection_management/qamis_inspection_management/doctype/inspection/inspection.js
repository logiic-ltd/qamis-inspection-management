frappe.ui.form.on('Inspection', {
    refresh: function(frm) {
        frm.add_custom_button(__('Add Team'), function() {
            show_team_management_dialog(frm);
        });
        frm.add_custom_button(__('Add Checklist'), function() {
            show_checklist_search_dialog(frm);
        });
    },
    teams_add: function(frm) {
        frm.fields_dict.teams.grid.get_field('team_name').get_query = function() {
            return {
                filters: {
                    'docstatus': 1
                }
            };
        };
    }
});

function show_team_management_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: 'Add Team',
        fields: [
            {
                fieldname: 'team_name',
                fieldtype: 'Data',
                label: 'Team Name',
                reqd: 1
            },
            {
                fieldname: 'team_members_and_schools_section',
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
                cannot_add_rows: true,
                fields: [
                    {
                        fieldname: 'id',
                        fieldtype: 'Data',
                        label: 'ID',
                        in_list_view: 1,
                        read_only: 1
                    },
                    {
                        fieldname: 'schoolName',
                        fieldtype: 'Data',
                        label: 'School Name',
                        in_list_view: 1,
                        read_only: 1
                    },
                    {
                        fieldname: 'province',
                        fieldtype: 'Data',
                        label: 'Province',
                        in_list_view: 1,
                        read_only: 1
                    },
                    {
                        fieldname: 'district',
                        fieldtype: 'Data',
                        label: 'District',
                        in_list_view: 1,
                        read_only: 1
                    }
                ]
            }
        ],
        primary_action_label: 'Add Team',
        primary_action(values) {
            add_team_to_inspection(frm, values);
            d.hide();
            frm.refresh();
        }
    });

    d.$wrapper.find('.modal-dialog').css("max-width", "80%");

    // Initialize search functionality
    init_member_search(d);
    init_school_search(d);
    
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
                            add_member_to_selection(dialog, {
                                id: item.id,
                                displayName: item.displayName,
                                username: item.username
                            });
                            $results.empty();
                            $search_input.val('');
                        });
                    } else {
                        $results.html('<p>No results found</p>');
                    }
                }
            });
        }, 300);
    });

    $search_input.on('change', function() {
        if ($search_input.val() === '') {
            $results.empty();
        }
    });

    $search_input.on('input', function() {
        if ($search_input.val() === '') {
            $results.empty();
        }
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
                            add_school_to_selection(dialog, {
                                id: item.id || item.schoolCode,  // Use schoolCode as fallback
                                schoolName: item.schoolName,
                                province: item.province,
                                district: item.district
                            });
                        });
                    } else {
                        $results.html('<p>No results found or unable to connect to the API. Please try again later.</p>');
                    }
                }
            });
        }, 300);
    });

    $search_input.on('input', function() {
        if ($search_input.val() === '') {
            $results.empty();
        }
    });
}

function add_school_to_selection(dialog, school) {
    let grid = dialog.fields_dict.selected_schools.grid;
    let existing_school = grid.data.find(s => s.id === school.id);
    
    if (!existing_school) {
        let new_row = {
            id: school.id,
            schoolName: school.schoolName,
            province: school.province,
            district: school.district
        };
        grid.add_new_row();
        let added_row = grid.data[grid.data.length - 1];
        Object.assign(added_row, new_row);
        
        grid.refresh();
        dialog.fields_dict.school_search.$input.val('').trigger('input');
    } else {
        frappe.show_alert(`${school.schoolName} is already in the team.`, 5);
    }
}

function add_member_to_selection(dialog, member) {
    let grid = dialog.fields_dict.selected_members.grid;
    let existing_member = grid.data.find(m => m.id === member.id);
    
    if (!existing_member) {
        let new_row = {
            id: member.id,
            displayName: member.displayName,
            username: member.username
        };
        grid.add_new_row();
        let added_row = grid.data[grid.data.length - 1];
        Object.assign(added_row, new_row);
        
        grid.refresh();
    } else {
        frappe.show_alert(`${member.displayName} is already in the team.`, 5);
    }
}

function add_school_to_selection(dialog, school) {
    let table = dialog.fields_dict.selected_schools;
    let existing_school = table.get_data().find(s => s.id === school.id);
    
    if (!existing_school) {
        let new_row = {
            id: school.id,
            schoolName: school.schoolName,
            province: school.province,
            district: school.district
        };
        table.df.data.push(new_row);
        table.refresh();
    } else {
        frappe.show_alert(`${school.schoolName} is already in the team.`, 5);
    }
}

function adjust_table_columns(dialog) {
    const tables = ['selected_members', 'selected_schools', 'teams'];
    tables.forEach(table => {
        const grid = dialog.fields_dict[table].grid;
        if (grid) {
            grid.columns.forEach(column => {
                if (column.df.fieldname === 'id') {
                    column.df.width = 100;
                } else {
                    column.df.width = 300;
                }
            });
            grid.setup_columns();
            grid.refresh();
        }
    });
}

function add_team_to_inspection(frm, values) {
    let team_name = values.team_name;
    let selected_members = values.selected_members || [];
    let selected_schools = values.selected_schools || [];

    if (!team_name || selected_members.length === 0 || selected_schools.length === 0) {
        frappe.msgprint('Please enter a team name, select at least one member and one school.');
        return;
    }

    let new_team = {
        team_name: team_name,
        members: selected_members,
        schools: selected_schools,
        schools_count: selected_schools.length,
        members_count: selected_members.length
    };

    frm.doc.teams = frm.doc.teams || [];
    frm.add_child('teams', new_team);

    frm.refresh_field('teams');
    frappe.show_alert(`Team "${team_name}" added successfully`, 5);
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
