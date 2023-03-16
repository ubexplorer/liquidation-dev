# Copyright 2018, 2021 Heliconia Solutions Pvt Ltd (https://heliconia.io)

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_rent_lot_sequense = fields.Boolean(
        string="Автонумерація лотів з оренди?",
        config_parameter="dgf_auction.use_rent_lot_sequense",
    )
    rent_lot_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Послідовність лотів з оренди",
        copy=False,
        readonly=False,
    )
    use_sale_lot_sequense = fields.Boolean(
        string="Автонумерація лотів з продажу?",
        config_parameter="dgf_auction.use_rent_lot_sequense",
    )
    sale_lot_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Послідовність лотів з продажу",
        copy=False,
        readonly=False,
    )
    reminder_before_day = fields.Integer(string="Send reminder before days")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        rent_lot_sequence_id = IrConfigParameter.get_param("dgf_auction.rent_lot_sequence_id")
        sale_lot_sequence_id = IrConfigParameter.get_param("dgf_auction.sale_lot_sequence_id")
        reminder_before_day = IrConfigParameter.get_param("dgf_auction.reminder_before_day")
        res.update(
            rent_lot_sequence_id=int(rent_lot_sequence_id),
            sale_lot_sequence_id=int(sale_lot_sequence_id),
            reminder_before_day=int(reminder_before_day),
        )
        return res

    def set_values(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        super(ResConfigSettings, self).set_values()
        IrConfigParameter.set_param("dgf_auction.rent_lot_sequence_id", self.rent_lot_sequence_id.id or False)
        IrConfigParameter.set_param("dgf_auction.sale_lot_sequence_id", self.sale_lot_sequence_id.id or False)
        IrConfigParameter.set_param("dgf_auction.reminder_before_day", self.reminder_before_day or 0)
