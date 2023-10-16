# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class BaseTypeAbstract(models.AbstractModel):
    """Inherit from this class to add support for Types to your model.
    All public properties are preceded with type_ in order to isolate from
    child models, with the exception of: type_id, which is a required field in
    the Kanban widget and must be defined as such, and user_id, which is a
    special field that has special treatment in some places (such as the
    mail module).
    """

    _name = "base.type.abstract"
    _description = "Type Abstract"
    _order = "kanban_priority desc, sequence"
    _group_by_full = {
        "type_id": lambda s, *a, **k: s._read_group_stage_ids(*a, **k),
    }

    type_sequence = fields.Integer(default=10, index=True)
    type_id = fields.Many2one(
        string="Тип",
        comodel_name="dgf.base.type",
        tracking=True,
        index=True,
        copy=False,
        domain=lambda s: [("res_model_id.model", "=", s._name)],
        group_expand="_read_group_type_ids", # 
    )
    user_id = fields.Many2one(
        string="Assigned To",
        comodel_name="res.users",
        index=True,
        tracking=True,
        help="User that the record is currently assigned to",
    )



    def _valid_field_parameter(self, field, name):
        # allow tracking on models inheriting from this model
        return name == "tracking" or super()._valid_field_parameter(field, name)

    def _read_group_type_ids(self, types, domain, order):
        search_domain = [("res_model_id.model", "=", self._name)]
        return types.search(search_domain, order=order)
