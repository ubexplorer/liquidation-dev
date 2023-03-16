# Copyright 2018, 2021 Heliconia Solutions Pvt Ltd (https://heliconia.io)

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_lot_sequense = fields.Boolean(
        string="Використовувати автонумерацію лотів?",
        config_parameter="dgf_auction.use_lot_sequense",
    )
    lot_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Послідовність",
        copy=False,
        readonly=False,
    )
    reminder_before_day = fields.Integer(string="Send reminder before days")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        lot_sequence_id = IrConfigParameter.get_param(
            "dgf_auction.lot_sequence_id"
        )
        reminder_before_day = IrConfigParameter.get_param(
            "dgf_auction.reminder_before_day"
        )
        res.update(
            lot_sequence_id=int(lot_sequence_id),
            reminder_before_day=int(reminder_before_day),
        )
        return res

    def set_values(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        super(ResConfigSettings, self).set_values()
        IrConfigParameter.set_param(
            "dgf_auction.lot_sequence_id", self.lot_sequence_id.id or False
        )
        IrConfigParameter.set_param(
            "dgf_auction.reminder_before_day", self.reminder_before_day or 0
        )
