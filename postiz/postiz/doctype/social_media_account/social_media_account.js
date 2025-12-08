// Copyright (c) 2025, Abhishek and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Social Media Account", {
// 	refresh(frm) {

// 	},
// });
// frappe.ui.form.on("Social Media Account", {
//     refresh(frm) {

//         // Only show button if account is NOT connected
//         if (!frm.doc.connected) {

//             frm.add_custom_button("Connect X Account", () => {

//                 if (!frm.doc.channel) {
//                     frappe.msgprint("Please select a Channel first (e.g., X).");
//                     return;
//                 }

//                 // Redirect to OAuth start
//                 window.location.href = `/api/method/postiz.postiz.api.oauth.start?channel=${frm.doc.channel}`;

//             }).addClass("btn-primary");
//         }

//         // If connected, show a confirmation label
//         if (frm.doc.connected) {
//             frm.dashboard.set_headline_alert(`Connected as @${frm.doc.user_handle}`, 'alert-success');
//         }
//     }
// });

frappe.ui.form.on("Social Media Account", {
    refresh(frm) {
        // Only show button if account is NOT connected
        if (!frm.doc.connected) {
            frm.add_custom_button("Connect Account", () => {
                if (!frm.doc.channel) {
                    frappe.msgprint("Please select a Channel first (e.g., Youtube).");
                    return;
                }

                // Redirect to OAuth start
                window.location.href = `/api/method/postiz.api.oauth.start?channel=YouTube`;
            }).addClass("btn-primary");
        }

        // If connected, show a confirmation label
        if (frm.doc.connected) {
            frm.dashboard.set_headline_alert(`Connected as ${frm.doc.user_name}`, 'alert-success');
        }
    }
});