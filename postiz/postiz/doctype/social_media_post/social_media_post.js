frappe.ui.form.on('Social Media Post', {
    refresh: function (frm) {

        // custom buttons based on status
        if (frm.doc.status === 'Draft' && !frm.is_new()) {
            // frm.page.btn_primary.hide();
            frm.add_custom_button(__('Schedule Post'), function () {
                schedule_post(frm);
            }).addClass('btn_primary');
        }

        if (frm.doc.status === 'Scheduled') {
            frm.add_custom_button(__('Cancel Schedule'), function () {
                cancel_scheduled_post(frm);
            }, __('Actions'));

            frm.add_custom_button(__('Refresh Status'), function () {
                refresh_post_status(frm);
            }, __('Actions'));
        }

        // indicator colors
        if (frm.doc.status) {
            frm.page.set_indicator(frm.doc.status, get_status_color(frm.doc.status));
        }

        // Make fields read-only if scheduled or published
        // if (['Scheduled', 'Published'].includes(frm.doc.status)) {
        //     frm.set_df_property('content', 'read_only', 1);
        //     frm.set_df_property('scheduled_time', 'read_only', 1);
        //     frm.set_df_property('platforms', 'read_only', 1);
        //     frm.set_df_property('media', 'read_only', 1);
        // }
    },

    // status: function (frm) {
    //     // Update indicator when status changes
    //     if (frm.doc.status) {
    //         frm.page.set_indicator(frm.doc.status, get_status_color(frm.doc.status));
    //     }
    // }
});

function schedule_post(frm) {
    // Validate required fields
    if (!frm.doc.scheduled_time) {
        frappe.msgprint(__('Please set a scheduled time'));
        return;
    }

    if (!frm.doc.platforms || frm.doc.platforms.length === 0) {
        frappe.msgprint(__('Please select at least one platform'));
        return;
    }


    frappe.confirm(
        __('Are you sure you want to schedule this post?'),
        function () {
            frappe.call({
                method: 'postiz.api.post_scheduler.schedule_post',
                args: {
                    post_id: frm.doc.name
                },
                freeze: true,
                freeze_message: __('Scheduling post...'),
                callback: function (r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'green'
                        });
                        frm.reload_doc();

                        // Auto-refresh status after 5 seconds
                        setTimeout(function () {
                            refresh_post_status(frm);
                        }, 5000);
                    } else {
                        frappe.msgprint({
                            title: __('Error'),
                            message: r.message ? r.message.message : __('Failed to schedule post'),
                            indicator: 'red'
                        });
                    }
                },
                error: function (err) {
                    frappe.msgprint({
                        title: __('Error'),
                        message: __('An error occurred while scheduling the post'),
                        indicator: 'red'
                    });
                }
            });
        }
    );
}

function cancel_scheduled_post(frm) {
    frappe.confirm(
        __('Are you sure you want to cancel this scheduled post?'),
        function () {
            frappe.call({
                method: 'postiz.api.post_scheduler.cancel_scheduled_post',
                args: {
                    post_id: frm.doc.name
                },
                freeze: true,
                freeze_message: __('Cancelling post...'),
                callback: function (r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'orange'
                        });
                        frm.reload_doc();
                    } else {
                        frappe.msgprint({
                            title: __('Error'),
                            message: r.message ? r.message.message : __('Failed to cancel post'),
                            indicator: 'red'
                        });
                    }
                }
            });
        }
    );
}

function refresh_post_status(frm) {
    frappe.call({
        method: 'postiz.api.post_scheduler.get_post_status',
        args: {
            post_id: frm.doc.name
        },
        callback: function (r) {
            if (r.message && r.message.success) {
                frappe.show_alert({
                    message: __('Status: {0}', [r.message.status]),
                    indicator: 'blue'
                });
                frm.reload_doc();
            }
        }
    });
}

function get_status_color(status) {
    const status_colors = {
        'Draft': 'gray',
        'Scheduling': 'blue',
        'Scheduled': 'orange',
        'Published': 'green',
        'Failed': 'red',
        'Cancelled': 'darkgray'
    };
    return status_colors[status] || 'gray';
}