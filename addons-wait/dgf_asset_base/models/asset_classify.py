# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AssetClassify(models.Model):
    _name = "asset.classify"
    _description = "Класифікатори активів"
    _order = "res_model_id, sequence"

    name = fields.Char(
        string="Name",
        translate=True,
        required=True,
        help="Displayed as the header for this stage in views",
    )
    code = fields.Char()
    description = fields.Text(
        translate=True,
        help="Short description of the stage's meaning/purpose",
    )
    sequence = fields.Integer(
        default=1,
        required=True,
        index=True,
        help="Order of stage in relation to other stages available for the"
        " same model",
    )
    fold = fields.Boolean(
        string="Collapse?",
        help="Determines whether this stage will be collapsed down in views",
    )
    res_model_id = fields.Many2one(
        string="Associated Model",
        comodel_name="ir.model",
        required=True,
        index=True,
        help="The model that this stage will be used for",
        # domain=["&", ("is_base_stage", "=", True), ("transient", "=", False)],
        default=lambda s: s._default_res_model_id(),
        ondelete="cascade",
    )
    # field_id = fields.Many2one(
    #     comodel_name='ir.model.fields',
    #     # domain=[('model', '=', res_model_id.model)],
    #     ondelete='cascade',
    # )
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=lambda s: s._mail_template_domain(),
        help="If set an email will be sent to the customer when the task or issue reaches this step.")
    is_closed = fields.Boolean(
        'Closing Stage', help="Tasks in this stage are considered as closed.")
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")

    @api.model
    def _default_res_model_id(self):
        """Useful when creating stages from a view for another model"""
        action_id = self.env.context.get("params", {}).get("action")
        action = self.env["ir.actions.act_window"].browse(action_id)
        default_model = action.res_model
        if default_model != self._name:
            return self.env["ir.model"].search([("model", "=", default_model)])

    @api.model
    def _mail_template_domain(self):
        """Useful when creating stages from a view for another model"""
        res_model_id = self.env.context.get('default_res_model_id')
        domain = [('model_id', '=', res_model_id)] if res_model_id is not False else []
        return domain
