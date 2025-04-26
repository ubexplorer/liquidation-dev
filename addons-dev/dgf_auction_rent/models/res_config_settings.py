# Copyright 2018, 2021 Heliconia Solutions Pvt Ltd (https://heliconia.io)

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_sale_lot_sequense = fields.Boolean(
        string="Автонумерація лотів з продажу?",
        config_parameter="dgf_auction_sale.use_sale_lot_sequense",
    )
    sale_lot_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Послідовність лотів з продажу",
        copy=False,
        readonly=False,
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        sale_lot_sequence_id = IrConfigParameter.get_param("dgf_auction_sale.sale_lot_sequence_id")
        res.update(
            sale_lot_sequence_id=int(sale_lot_sequence_id),
        )
        return res

    def set_values(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        super(ResConfigSettings, self).set_values()
        IrConfigParameter.set_param("dgf_auction_sale.sale_lot_sequence_id", self.sale_lot_sequence_id.id or False)
