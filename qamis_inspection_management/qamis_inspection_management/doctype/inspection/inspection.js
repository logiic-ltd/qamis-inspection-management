frappe.ui.form.on('Inspection', {
    refresh: function(frm) {
        frm.add_custom_button(__('Add Team Member'), function() {
            show_user_search_dialog(frm);
        });
    }
});

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
        user_id: user.id,
        username: user.username,
        display_name: user.displayName
    });
    frm.refresh_field('team_members');
    frm.save();
    frappe.show_alert(`Added ${user.displayName} to the team`, 5);
}
