# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_customer = fields.Boolean(
        compute="_compute_is_customer",
        inverse="_inverse_is_customer",
        store=True,
        readonly=False,
        string="Is a Customer",
        default=lambda self: self._default_is_customer(),
    )
    is_supplier = fields.Boolean(
        compute="_compute_is_supplier",
        inverse="_inverse_is_supplier",
        store=True,
        readonly=False,
        string="Is a Supplier",
        default=lambda self: self._default_is_supplier(),
    )

    @api.depends("customer_rank")
    def _compute_is_customer(self):
        for partner in self:
            if not partner.is_customer:
                partner.is_customer = bool(partner.customer_rank)

    @api.depends("supplier_rank")
    def _compute_is_supplier(self):
        for partner in self:
            if not partner.is_supplier:
                partner.is_supplier = bool(partner.supplier_rank)

    def _inverse_is_customer(self):
        self.filtered(lambda p: not p.is_customer).write({"customer_rank": 0})
        self.filtered(lambda p: p.is_customer and not p.customer_rank).write(
            {"customer_rank": 1}
        )

    def _inverse_is_supplier(self):
        self.filtered(lambda p: not p.is_supplier).write({"supplier_rank": 0})
        self.filtered(lambda p: p.is_supplier and not p.supplier_rank).write(
            {"supplier_rank": 1}
        )

    def _default_is_customer(self):
        return self.env.context.get("res_partner_search_mode") == "customer"

    def _default_is_supplier(self):
        return self.env.context.get("res_partner_search_mode") == "supplier"
