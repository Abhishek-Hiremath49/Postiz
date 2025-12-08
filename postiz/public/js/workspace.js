// // your_app/public/js/workspace.js
// frappe.provide('frappe.post_scheduler');

// // Global function for workspace onclick (unchanged)
// window.add_channel_dialog = function () {
//     frappe.post_scheduler.add_channel_dialog();
// };

// // Enhanced dialog using Frappe UI components
// frappe.post_scheduler.add_channel_dialog = function () {
//     const channels = [
//         { id: 'x', label: 'X (Twitter)', icon: 'https://cdn.jsdelivr.net/npm/simple-icons@v8/icons/twitter.svg', desc: 'Post to your X account' },
//         { id: 'linkedin', label: 'LinkedIn', icon: 'https://cdn.jsdelivr.net/npm/simple-icons@v8/icons/linkedin.svg', desc: 'Share on LinkedIn profile/page' },
//         { id: 'facebook', label: 'Facebook', icon: 'https://cdn.jsdelivr.net/npm/simple-icons@v8/icons/facebook.svg', desc: 'Post to Facebook Page' },
//         { id: 'instagram', label: 'Instagram', icon: 'https://cdn.jsdelivr.net/npm/simple-icons@v8/icons/instagram.svg', desc: 'Schedule Instagram posts' }
//     ];

//     // Build body using Frappe's html templating for grid
//     let body_html = '<div class="frappe-card channels-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; padding: 16px;">';
//     channels.forEach(channel => {
//         body_html += `
//             <div class="frappe-card channel-item" data-channel="${channel.id}" style="text-align: center; padding: 16px; border-radius: 4px; cursor: pointer; transition: var(--bg-color-transition);">
//                 <img src="${channel.icon}" alt="${channel.label}" style="width: 48px; height: 48px; margin-bottom: 8px; filter: var(--icon-color);" />
//                 <h6 style="margin: 8px 0; font-weight: 500;">${channel.label}</h6>
//                 <p style="color: var(--text-muted); font-size: 0.875rem; margin: 0;">${channel.desc}</p>
//             </div>
//         `;
//     });
//     body_html += '</div>';

//     const dialog = new frappe.ui.Dialog({
//         title: __('Add Channel'),
//         size: 'medium',  // Balanced for grid
//         body: body_html,  // Use templated HTML
//         static_area: 'body',  // Render in body for better positioning
//         render: function () {
//             // Attach event listeners using Frappe's event system
//             this.$wrapper.find('.channel-item').on('click', function () {
//                 const channel_id = $(this).data('channel');
//                 frappe.post_scheduler.handle_channel_select(channel_id, dialog);
//             });

//             // Frappe-style hover effects via CSS classes
//             this.$wrapper.find('.channel-item').hover(
//                 function () { $(this).addClass('hovered'); },
//                 function () { $(this).removeClass('hovered'); }
//             );

//             // Add CSS for hover (injected dynamically)
//             frappe.dom.set_style('.channel-item.hovered', 'background-color: var(--gray-50); transform: translateY(-2px);', this.$wrapper);
//         },
//         primary_action_label: __('Close'),
//         primary_action: () => dialog.hide()
//     });

//     dialog.show();
// };

// // Handler for channel selection (extensible)
// frappe.post_scheduler.handle_channel_select = function (channel_id, dialog) {
//     // Close current dialog
//     dialog.hide();

//     // Example: Open a Frappe form for auth (customize per channel)
//     const auth_fields = [
//         { label: __('Account Name'), fieldname: 'account_name', fieldtype: 'Data', reqd: 1 },
//         { label: __('Access Token'), fieldname: 'access_token', fieldtype: 'Password', reqd: 1 }
//     ];

//     const auth_dialog = new frappe.ui.Dialog({
//         title: __(channel_id.charAt(0).toUpperCase() + channel_id.slice(1) + ' Auth'),
//         fields: auth_fields,
//         primary_action_label: __('Save Channel'),
//         primary_action(values) {
//             // Save to doctype (e.g., Social Channel)
//             frappe.call({
//                 method: 'your_app.api.create_social_channel',  // Define in Python
//                 args: { channel_type: channel_id, ...values },
//                 callback: (r) => {
//                     if (r.message) {
//                         frappe.msgprint(__('Channel added successfully!'));
//                         frappe.set_route('List', 'Social Channel');  // Redirect to list
//                     }
//                 }
//             });
//             auth_dialog.hide();
//         }
//     });
//     auth_dialog.show();
// };