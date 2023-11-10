odoo.define('kw_sms_api.fields', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var _t = core._t;

var Phone = require("sms.fields");
Phone.include({
_onClickSMS: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();

        var context = session.user_context;
        context = _.extend({}, context, {
            default_res_model: this.model,
            default_res_id: parseInt(this.res_id),
            default_number_field_name: this.name,
            default_composition_mode: 'mass',
            default_mass_keep_log: true,
        });
        var self = this;
        return this.do_action({
            title: _t('Send SMS Text Message'),
            type: 'ir.actions.act_window',
            res_model: 'sms.composer',
            target: 'new',
            views: [[false, 'form']],
            context: context,
            binding_model_id: 'base.model_res_partner',
            binding_view_types: 'form'
        }, {
        on_close: function () {
            self.trigger_up('reload');
        }});
    },
});

return Phone;
});
