// frappe.ui.form.on('Social Media Post', {
//     refresh: function (frm) {

//         // custom buttons based on status
//         if (frm.doc.status === 'Draft' && !frm.is_new()) {
//             // frm.page.btn_primary.hide();
//             frm.add_custom_button(__('Schedule Post'), function () {
//                 schedule_post(frm);
//             }).addClass('btn_primary');
//         }

//         if (frm.doc.status === 'Scheduled') {
//             frm.add_custom_button(__('Cancel Schedule'), function () {
//                 cancel_scheduled_post(frm);
//             }, __('Actions'));

//             frm.add_custom_button(__('Refresh Status'), function () {
//                 refresh_post_status(frm);
//             }, __('Actions'));
//         }

//         // indicator colors
//         if (frm.doc.status) {
//             frm.page.set_indicator(frm.doc.status, get_status_color(frm.doc.status));
//         }

//         // Make fields read-only if scheduled or published
//         // if (['Scheduled', 'Published'].includes(frm.doc.status)) {
//         //     frm.set_df_property('content', 'read_only', 1);
//         //     frm.set_df_property('scheduled_time', 'read_only', 1);
//         //     frm.set_df_property('platforms', 'read_only', 1);
//         //     frm.set_df_property('media', 'read_only', 1);
//         // }
//     },

//     // status: function (frm) {
//     //     // Update indicator when status changes
//     //     if (frm.doc.status) {
//     //         frm.page.set_indicator(frm.doc.status, get_status_color(frm.doc.status));
//     //     }
//     // }
// });

// function schedule_post(frm) {
//     // Validate required fields
//     if (!frm.doc.scheduled_time) {
//         frappe.msgprint(__('Please set a scheduled time'));
//         return;
//     }

//     if (!frm.doc.platforms || frm.doc.platforms.length === 0) {
//         frappe.msgprint(__('Please select at least one platform'));
//         return;
//     }


//     frappe.confirm(
//         __('Are you sure you want to schedule this post?'),
//         function () {
//             frappe.call({
//                 method: 'postiz.api.post_scheduler.schedule_post',
//                 args: {
//                     post_id: frm.doc.name
//                 },
//                 freeze: true,
//                 freeze_message: __('Scheduling post...'),
//                 callback: function (r) {
//                     if (r.message && r.message.success) {
//                         frappe.show_alert({
//                             message: r.message.message,
//                             indicator: 'green'
//                         });
//                         frm.reload_doc();

//                         // Auto-refresh status after 5 seconds
//                         setTimeout(function () {
//                             refresh_post_status(frm);
//                         }, 5000);
//                     } else {
//                         frappe.msgprint({
//                             title: __('Error'),
//                             message: r.message ? r.message.message : __('Failed to schedule post'),
//                             indicator: 'red'
//                         });
//                     }
//                 },
//                 error: function (err) {
//                     frappe.msgprint({
//                         title: __('Error'),
//                         message: __('An error occurred while scheduling the post'),
//                         indicator: 'red'
//                     });
//                 }
//             });
//         }
//     );
// }

// function cancel_scheduled_post(frm) {
//     frappe.confirm(
//         __('Are you sure you want to cancel this scheduled post?'),
//         function () {
//             frappe.call({
//                 method: 'postiz.api.post_scheduler.cancel_scheduled_post',
//                 args: {
//                     post_id: frm.doc.name
//                 },
//                 freeze: true,
//                 freeze_message: __('Cancelling post...'),
//                 callback: function (r) {
//                     if (r.message && r.message.success) {
//                         frappe.show_alert({
//                             message: r.message.message,
//                             indicator: 'orange'
//                         });
//                         frm.reload_doc();
//                     } else {
//                         frappe.msgprint({
//                             title: __('Error'),
//                             message: r.message ? r.message.message : __('Failed to cancel post'),
//                             indicator: 'red'
//                         });
//                     }
//                 }
//             });
//         }
//     );
// }

// function refresh_post_status(frm) {
//     frappe.call({
//         method: 'postiz.api.post_scheduler.get_post_status',
//         args: {
//             post_id: frm.doc.name
//         },
//         callback: function (r) {
//             if (r.message && r.message.success) {
//                 frappe.show_alert({
//                     message: __('Status: {0}', [r.message.status]),
//                     indicator: 'blue'
//                 });
//                 frm.reload_doc();
//             }
//         }
//     });
// }

// function get_status_color(status) {
//     const status_colors = {
//         'Draft': 'gray',
//         'Scheduling': 'blue',
//         'Scheduled': 'orange',
//         'Published': 'green',
//         'Failed': 'red',
//         'Cancelled': 'darkgray'
//     };
//     return status_colors[status] || 'gray';
// }

// frappe.ui.form.on("Social Media Platform", {
//     platforms(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];

//         if (!row.platforms) return;

//         frappe.call({
//             method: "postiz.api.integrations.get_integration_by_platform",
//             args: { platform: row.platforms },
//             callback: function (r) {
//                 if (!r.message) return;

//                 if (r.message.integration_id) {
//                     row.integration_id = r.message.integration_id;

//                     // 🔥 Refresh only this field in the row
//                     frm.refresh_field("platforms");

//                     frappe.show_alert({
//                         message: __("Integration ID fetched successfully"),
//                         indicator: "green"
//                     });
//                 }
//                 else {
//                     frappe.msgprint({
//                         title: __("Not Found"),
//                         indicator: "red",
//                         message: __("No Integration ID found for platform: " + row.platforms)
//                     });
//                 }
//             }
//         });
//     },

//     content: function (frm, cdt, cdn) {
//         let row = locals[cdt][cdn];

//         // Define character limits
//         const LIMITS = {
//             "X": 2,
//             "Instagram": 5,
//             "LinkedIn": 13,
//             "Facebook": 20,
//             "Threads": 500,
//             "Youtube": 5000,
//             "Reddit": 30000,
//             "Mastodon": 500
//         };

//         if (!row.platforms) return;

//         const maxLen = LIMITS[row.platforms] || 500; // default fallback
//         const curLen = (row.content || "").length;

//         if (curLen > maxLen) {

//             // Trim the text automatically
//             row.content = row.content.substring(0, maxLen);
//             frappe.model.set_value(cdt, cdn, "content", row.content);

//             // Show ONE SINGLE message
//             frappe.msgprint({
//                 title: "Character Limit Exceeded",
//                 indicator: "red",
//                 message: `${row.platforms} allows only <b>${maxLen}</b> characters. Extra content has been removed.`
//             });
//         }
//     }
// });

// frappe.ui.form.on("Social Media Post", {
//     refresh: function (frm) {
//         if (frm.doc.status === "Draft") {
//             frm.add_custom_button(__('Schedule Post'), function () {
//                 // call schedule_post server method which will mark Scheduling and call scheduler (or external)
//                 frappe.call({
//                     method: "postiz.api.post_scheduler.manual_schedule",
//                     args: { post_id: frm.doc.name },
//                     callback: function (r) {
//                         if (r.message && r.message.success) {
//                             frm.reload_doc();
//                             frappe.msgprint(r.message.message || "Scheduled");
//                         } else {
//                             frappe.msgprint(r.message || "Scheduling failed");
//                         }
//                     }
//                 });
//             }).addClass('btn-primary');
//         }
//     }
// });

// frappe.ui.form.on("Social Media Post", {
//     refresh(frm) {

//         // Add POST NOW button when post is Draft
//         if (frm.doc.status === "Draft" && !frm.is_new()) {
//             frm.add_custom_button("Post Now", function () {
//                 frappe.confirm(
//                     "Post this video to YouTube immediately?",
//                     function () {
//                         frappe.call({
//                             method: "postiz.api.post_scheduler.post_now",
//                             args: { post_id: frm.doc.name },
//                             freeze: true,
//                             freeze_message: "Uploading video to YouTube...",
//                             callback(r) {
//                                 if (r.message && r.message.success) {
//                                     frappe.show_alert({
//                                         message: "Video posted successfully!",
//                                         indicator: "green"
//                                     });
//                                     frm.reload_doc();
//                                 } else {
//                                     frappe.show_alert({
//                                         message: r.message?.error || "Upload failed",
//                                         indicator: "red"
//                                     });
//                                 }
//                             }
//                         });
//                     }
//                 );
//             }, "Primary").addClass("btn-primary");
//         }

//         // Show status nicely
//         if (frm.doc.status === "Published") {
//             frm.dashboard.set_headline_alert("Posted to YouTube", "alert-success");
//         }
//     }
// });

frappe.ui.form.on("Social Media Post", {
    refresh(frm) {
        // Always remove old buttons first
        // frm.remove_custom_button("Post Now");
        // frm.remove_custom_button("Schedule Post");

        // Only show buttons when in Draft
        if (frm.doc.status !== "Draft" || frm.is_new()) return;

        // Always show "Post Now" button
        frm.add_custom_button(__("Post Now"), function () {
            frappe.confirm("Publish this post immediately?", () => {
                frappe.call({
                    method: "postiz.api.post_scheduler.post_now",
                    args: { post_id: frm.doc.name },
                    freeze: true,
                    freeze_message: __("Uploading to YouTube..."),
                    callback(r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: "Posted successfully!",
                                indicator: "green"
                            });
                        } else {
                            frappe.show_alert({
                                message: r.message?.error || "Upload failed",
                                indicator: "red"
                            });
                        }
                        frm.reload_doc();
                    }
                });
            });
        }, __("Actions")).addClass("btn-primary");

        // Show "Schedule Post" only if scheduled_time is set
        if (frm.doc.scheduled_time) {
            frm.add_custom_button(__("Schedule Post"), function () {
                const time = frappe.datetime.str_to_user(frm.doc.scheduled_time);
                frappe.confirm(`Schedule this post for <b>${time}</b>?`, () => {
                    frm.set_value("status", "Scheduled");
                    frm.save("Submit").then(() => {
                        frappe.show_alert({
                            message: `Post scheduled for ${time}!`,
                            indicator: "green"
                        });
                    });
                });
            }, __("Actions")).addClass("btn-success");
        }

        // Visual indicator when already scheduled
        if (frm.doc.status === "Scheduled") {
            const time = frappe.datetime.str_to_user(frm.doc.scheduled_time);
            frm.dashboard.set_headline_alert(
                `Scheduled for: <b>${time}</b>`,
                "blue"
            );
        }

        if (frm.doc.status === "Published" && frm.doc.youtube_url) {
            frm.dashboard.set_headline_alert(
                `Published! <a href="${frm.doc.youtube_url}" target="_blank">Watch on YouTube</a>`,
                "green"
            );
        }
    },

    // Refresh buttons when user changes scheduled_time
    scheduled_time(frm) {
        frm.trigger("refresh");
    }
});