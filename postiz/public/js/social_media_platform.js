// // your_app/doctype/social_media_platform/social_media_platform.js

// frappe.ui.form.on("Social Media Platform", {
//     platforms: function (frm, cdt, cdn) {
//         let row = locals[cdt][cdn];

//         // When platform is selected, auto-fetch integrations from Postiz
//         frappe.call({
//             method: "postiz.api.integrations.fetch_postiz_integrations",
//             freeze: true,
//             callback: function (r) {
//                 if (!r.message || !r.message.integrations) return;

//                 let list = r.message.integrations;

//                 // Try to match Postiz integration "source" with ERPNext platform
//                 let match = list.find(i =>
//                     i.source.toLowerCase() === row.platforms.toLowerCase()
//                 );

//                 if (match) {
//                     row.integration_id = match.id;
//                     frm.refresh_field("platforms");
//                     frappe.msgprint(__("Integration ID auto-filled for " + row.platforms));
//                 } else {
//                     frappe.msgprint(__("No integration found in Postiz for " + row.platforms));
//                 }
//             }
//         });
//     }
// });
frappe.ui.form.on("Social Media Platform", {
    platforms: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (!row.platforms) return;

        // Map platforms label → Postiz identifier
        const PLATFORM_MAP = {
            "X": "x",
            "Youtube": "youtube",
            "Facebook": "facebook",
            "Instagram": "instagram",
            "LinkedIn": "linkedin",
            "Threads": "threads"
        };

        let identifier = PLATFORM_MAP[row.platforms];
        console.log("Loading integrations for:", identifier);

        frappe.call({
            method: "postiz.api.integrations.fetch_postiz_integrations",
            freeze: true,
            callback: function (r) {
                if (!r.message || !r.message.integrations) {
                    frappe.msgprint("Could not fetch integrations from Postiz");
                    return;
                }

                let list = r.message.integrations;

                // Find matching integration in Postiz response
                let match = list.find(i =>
                    (i.identifier || "").toLowerCase() === identifier.toLowerCase()
                );

                if (match) {
                    row.integration_id = match.id;
                    frm.refresh_field("platforms");

                    frappe.show_alert({
                        message: __("Integration ID found for {0}: {1}", [row.platforms, match.id]),
                        indicator: "green"
                    });
                } else {
                    frappe.msgprint(
                        __("No integration configured in Postiz for platform: {0}", [row.platforms])
                    );
                }
            }
        });
    }
});
