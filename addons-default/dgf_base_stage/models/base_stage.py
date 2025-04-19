# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class BaseStage(models.Model):
    _name = "base.stage"
    _description = "Stage"
    _order = "res_model_id, sequence"

    name = fields.Char(
        string="Stage Name",
        translate=False,
        required=True,
        help="Displayed as the header for this stage in views",
    )
    description = fields.Text(
        translate=False,
        help="Short description of the stage's meaning/purpose",
    )
    sequence = fields.Integer(
        default=1,
        required=True,
        index=True,
        help="Order of stage in relation to other stages available for the"
        " same model",
    )
    legend_priority = fields.Text(
        string="Priority Explanation",
        translate=True,
        default="Mark a card as medium or high priority (one or two stars) to"
        " indicate that it should be escalated ahead of others with"
        " lower priority/star counts.",
        help="Explanation text to help users understand how the priority/star"
        " mechanism applies to this stage",
    )
    legend_blocked = fields.Text(
        string="Special Handling Explanation",
        translate=True,
        default="Give a card the special handling status to indicate that it"
        " requires handling by a special user or subset of users.",
        help="Explanation text to help users understand how the special"
        " handling status applies to this stage",
    )
    legend_done = fields.Text(
        string="Ready Explanation",
        translate=True,
        default="Mark a card as ready when it has been fully processed.",
        help="Explanation text to help users understand how the ready status"
        " applies to this stage",
    )
    legend_normal = fields.Text(
        string="Normal Handling Explanation",
        translate=True,
        default="This is the default status and indicates that a card can be"
        " processed by any user working this queue.",
        help="Explanation text to help users understand how the normal"
        " handling status applies to this stage",
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
        domain=["&", ("is_stage", "=", True), ("transient", "=", False)],
        default=lambda s: s._default_res_model_id(),
        ondelete="cascade",
    )
    code = fields.Char()
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
