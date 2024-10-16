frappe.ui.form.on('Inspection', {
    refresh: function(frm) {
        frm.add_custom_button(__('Search Team Members'), function() {
            show_user_search_dialog(frm);
        });
    }
});

function show_user_search_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: 'Search Team Members',
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

    $search_input.on('input', frappe.utils.debounce(function() {
        let search_term = $search_input.val();
        if (search_term.length < 2) return;

        frappe.call({
            method: 'qamis_inspection_management.qamis_inspection_management.doctype.inspection.inspection.search_users',
            args: {
                search_term: search_term
            },
            callback: function(r) {
                if (r.message) {
                    let users = r.message;
                    let html = users.map(user => `
                        <div class="user-item" data-user='${JSON.stringify(user)}'>
                            <strong>${frappe.utils.escape_html(user.displayName)}</strong>
                            <br>
                            <small>${frappe.utils.escape_html(user.username)}</small>
                        </div>
                    `).join('');
                    $results.html(html);

                    $results.find('.user-item').on('click', function() {
                        let user = $(this).data('user');
                        add_team_member(frm, user);
                        d.hide();
                    });
                }
            }
        });
    }, 300));

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
}
