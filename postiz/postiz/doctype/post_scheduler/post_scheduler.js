// Copyright (c) 2025, Abhishek and contributors
// For license information, please see license.txt

frappe.ui.form.on("Post Scheduler", {
    refresh(frm) {

    },
});


// frappe.ui.form.on("Post Scheduler", {
//     validate(frm) {
//         // This runs when the form is saved
//         frappe.call({
//             method: "postiz.postiz.postiz.api.fast_api.call_fastapi",
//             args: {
//                 channel: frm.doc.channel,
//                 description: frm.doc.description,
//                 // schedule_date: frm.doc.schedule_date,
//                 // schedule_time: frm.doc.schedule_time
//             },
//             callback: function (r) {
//                 console.log("FastAPI Response:", r.message);

//                 frappe.show_alert({
//                     message: "Sent to FastAPI Successfully!",
//                     indicator: "green"
//                 });
//             }
//         });
//     }
// });
